from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Produto, Categoria
from .forms import ProdutoForm, CategoriaForm

@login_required
def produto_list(request):
    query = request.GET.get('q', '')
    produtos = Produto.objects.filter(ativo=True)
    if query:
        produtos = produtos.filter(nome__icontains=query)
    return render(request, 'products/list.html', {'produtos': produtos, 'query': query})

@login_required
def produto_create(request):
    form = ProdutoForm(request.POST or None)
    if form.is_valid():
        produto = form.save(commit=False)
        import uuid
        produto.sku = f"TEMP-{uuid.uuid4().hex[:8]}"
        if not produto.categoria_id:
            from .models import Categoria
            categoria_padrao, _ = Categoria.objects.get_or_create(
                nome="Geral",
                defaults={"descricao": "Categoria padrão criada automaticamente"}
            )
            produto.categoria = categoria_padrao
        produto.save()
        # Atualiza o SKU para ser o ID real do produto no banco
        produto.sku = str(produto.id)
        produto.save(update_fields=['sku'])
        
        messages.success(request, 'Produto criado com sucesso!')
        return redirect('produto-list')
    return render(request, 'products/form.html', {'form': form, 'titulo': 'Novo Produto'})

@login_required
def produto_update(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    form = ProdutoForm(request.POST or None, instance=produto)
    if form.is_valid():
        produto = form.save(commit=False)
        if not produto.categoria_id:
            from .models import Categoria
            categoria_padrao, _ = Categoria.objects.get_or_create(
                nome="Geral",
                defaults={"descricao": "Categoria padrão criada automaticamente"}
            )
            produto.categoria = categoria_padrao
        produto.save()
        messages.success(request, 'Produto atualizado com sucesso!')
        return redirect('produto-list')
    return render(request, 'products/form.html', {'form': form, 'titulo': f'Editar: {produto.nome}'})

@login_required
def produto_delete(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        produto.delete()
        messages.success(request, 'Produto excluído com sucesso!')
        return redirect('produto-list')
    return render(request, 'products/delete_confirm.html', {'produto': produto})

@login_required
def categoria_list(request):
    categorias = Categoria.objects.all().order_by('-criado_em')
    return render(request, 'products/categoria_list.html', {'categorias': categorias})

@login_required
def categoria_create(request):
    form = CategoriaForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Categoria criada com sucesso!')
        return redirect('categoria-list')
    return render(request, 'products/categoria_form.html', {'form': form, 'titulo': 'Nova Categoria'})

@login_required
def categoria_update(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    form = CategoriaForm(request.POST or None, instance=categoria)
    if form.is_valid():
        form.save()
        messages.success(request, 'Categoria atualizada com sucesso!')
        return redirect('categoria-list')
    return render(request, 'products/categoria_form.html', {'form': form, 'titulo': f'Editar Categoria: {categoria.nome}'})

@login_required
def categoria_delete(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        # Evitar exclusão de categorias que possuem produtos
        if categoria.produtos.exists():
            messages.error(request, 'Não é possível excluir uma categoria que possui produtos vinculados.')
            return redirect('categoria-list')
        categoria.delete()
        messages.success(request, 'Categoria excluída com sucesso!')
        return redirect('categoria-list')
    return render(request, 'products/delete_confirm.html', {'produto': categoria})