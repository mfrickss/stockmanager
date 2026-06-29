from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Count
from django.utils import timezone
from movements.models import Movimentacao
from products.models import Produto, Categoria
from datetime import timedelta

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
