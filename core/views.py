from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Sum, F, Count
from django.utils import timezone
from django.http import HttpResponse
from movements.models import Movimentacao
from products.models import Produto, Categoria
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.conf import settings


def login_view(request):
    """
    View de login customizada que gera JWT e armazena em cookies HttpOnly.
    Elimina completamente a necessidade de sessões no banco de dados.
    """
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Gerar tokens JWT
            refresh = RefreshToken.for_user(user)
            # Adicionar claims customizados ao access token
            refresh['username'] = user.username
            access_token = refresh.access_token
            access_token['username'] = user.username

            next_url = request.POST.get('next', '/')
            response = redirect(next_url if next_url else '/')

            # Setar cookies HttpOnly (não acessíveis via JavaScript)
            response.set_cookie(
                'access_token',
                str(access_token),
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME_SECONDS', 1800),
            )
            response.set_cookie(
                'refresh_token',
                str(refresh),
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME_SECONDS', 604800),
            )
            return response
        else:
            # Login falhou
            return render(request, 'auth/login.html', {
                'form': {'errors': True},
                'error_message': 'Nome de usuário ou senha incorretos.'
            })

    return render(request, 'auth/login.html')


def logout_view(request):
    """Remove os cookies JWT e redireciona para o login."""
    response = redirect('login')
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response


def register_view(request):
    """
    View de registro que cria o usuário e faz login automático via JWT.
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        errors = []
        form_data = {'username': username, 'email': email}

        # Validações
        if not username:
            errors.append('O nome de usuário é obrigatório.')
        elif User.objects.filter(username__iexact=username).exists():
            errors.append('Este nome de usuário já está em uso.')

        if password1 != password2:
            errors.append('As senhas não coincidem.')
        elif password1:
            try:
                validate_password(password1)
            except ValidationError as e:
                errors.extend(e.messages)

        if errors:
            return render(request, 'auth/register.html', {
                'errors': errors,
                'form_data': form_data,
            })

        # Criar usuário
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
        )

        # Auto-login via JWT
        refresh = RefreshToken.for_user(user)
        refresh['username'] = user.username
        access_token = refresh.access_token
        access_token['username'] = user.username

        response = redirect('dashboard')
        response.set_cookie(
            'access_token',
            str(access_token),
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
            max_age=settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME_SECONDS', 1800),
        )
        response.set_cookie(
            'refresh_token',
            str(refresh),
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
            max_age=settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME_SECONDS', 604800),
        )
        return response

    return render(request, 'auth/register.html')


@login_required
def dashboard(request):
    periodo = request.GET.get('periodo', 'mes')
    now = timezone.now()
    
    if periodo == 'hoje':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        periodo_label = "Hoje"
    elif periodo == '7dias':
        start_date = now - timedelta(days=7)
        periodo_label = "Últimos 7 dias"
    elif periodo == 'ano':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        periodo_label = "Este Ano"
    else:
        periodo = 'mes'
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        periodo_label = "Este Mês"
        
    movs = Movimentacao.objects.filter(criado_em__gte=start_date)
    
    entradas = movs.filter(tipo='ENTRADA')
    saidas = movs.filter(tipo='SAIDA')
    
    qtd_entrada = entradas.aggregate(total=Sum('quantidade'))['total'] or 0
    valor_entrada = entradas.annotate(valor_total=F('quantidade') * F('produto__preco')).aggregate(total=Sum('valor_total'))['total'] or 0
    
    qtd_saida = saidas.aggregate(total=Sum('quantidade'))['total'] or 0
    valor_saida = saidas.annotate(valor_total=F('quantidade') * F('produto__preco')).aggregate(total=Sum('valor_total'))['total'] or 0
    
    # Capital imobilizado (valor total do estoque atual, independente do filtro de tempo)
    capital_imobilizado = Produto.objects.filter(ativo=True).annotate(
        valor_estoque=F('quantidade_estoque') * F('preco')
    ).aggregate(total=Sum('valor_estoque'))['total'] or 0
    
    total_produtos_ativos = Produto.objects.filter(ativo=True).count()
    total_itens_estoque = Produto.objects.filter(ativo=True).aggregate(total=Sum('quantidade_estoque'))['total'] or 0
    
    # Top 5 produtos mais vendidos no período
    top_produtos = saidas.values(
        'produto__nome', 'produto__id'
    ).annotate(
        total_vendido=Sum('quantidade')
    ).order_by('-total_vendido')[:5]
    
    # Top 5 categorias mais vendidas no período
    top_categorias = saidas.values(
        'produto__categoria__nome', 'produto__categoria__id'
    ).annotate(
        total_vendido=Sum('quantidade')
    ).order_by('-total_vendido')[:5]
    
    # Produtos com estoque crítico (<= 10 unidades)
    estoque_critico = Produto.objects.filter(
        ativo=True, quantidade_estoque__lte=10
    ).order_by('quantidade_estoque')[:10]
    
    recentes = Movimentacao.objects.select_related('produto', 'responsavel').order_by('-criado_em')[:6]
    
    context = {
        'periodo': periodo,
        'periodo_label': periodo_label,
        'qtd_entrada': qtd_entrada,
        'valor_entrada': valor_entrada,
        'qtd_saida': qtd_saida,
        'valor_saida': valor_saida,
        'capital_imobilizado': capital_imobilizado,
        'total_produtos_ativos': total_produtos_ativos,
        'total_itens_estoque': total_itens_estoque,
        'top_produtos': top_produtos,
        'top_categorias': top_categorias,
        'estoque_critico': estoque_critico,
        'movimentacoes_recentes': recentes,
    }
    
    return render(request, 'dashboard.html', context)
