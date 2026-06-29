from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Movimentacao
from .forms import MovimentacaoForm

@login_required
def movimentacao_list(request):
    movimentacoes = Movimentacao.objects.select_related('produto', 'responsavel').order_by('-criado_em')
    return render(request, 'movements/list.html', {'movimentacoes': movimentacoes})

@login_required
def movimentacao_create(request):
    form = MovimentacaoForm(request.POST or None)
    if form.is_valid():
        movimentacao = form.save(commit=False)
        movimentacao.responsavel = request.user
        
        produto = movimentacao.produto
        # Validação de estoque para saídas
        if movimentacao.tipo == 'SAIDA' and produto.quantidade_estoque < movimentacao.quantidade:
            messages.error(request, f'Estoque insuficiente! O produto {produto.nome} tem apenas {produto.quantidade_estoque} em estoque.')
            return render(request, 'movements/form.html', {'form': form, 'titulo': 'Nova Movimentação'})
            
        # Atualiza a quantidade do produto
        if movimentacao.tipo == 'ENTRADA':
            produto.quantidade_estoque += movimentacao.quantidade
        elif movimentacao.tipo == 'SAIDA':
            produto.quantidade_estoque -= movimentacao.quantidade
            
        produto.save(update_fields=['quantidade_estoque'])
        movimentacao.save()
        
        messages.success(request, 'Movimentação registrada com sucesso!')
        return redirect('movimentacao-list')
        
    return render(request, 'movements/form.html', {'form': form, 'titulo': 'Nova Movimentação'})
