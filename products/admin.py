from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Categoria, Produto

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'sku', 'categoria', 'quantidade_estoque', 'ativo']
    list_filter = ['categoria', 'ativo']
    search_fields = ['nome', 'sku']

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'criado_em']