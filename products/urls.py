from django.urls import path
from . import views

urlpatterns = [
    path('',               views.produto_list,   name='produto-list'),
    path('novo/',          views.produto_create,  name='produto-create'),
    path('<int:pk>/editar/', views.produto_update, name='produto-update'),
    path('<int:pk>/deletar/', views.produto_delete, name='produto-delete'),
    
    # Categorias
    path('categorias/', views.categoria_list, name='categoria-list'),
    path('categorias/nova/', views.categoria_create, name='categoria-create'),
    path('categorias/<int:pk>/editar/', views.categoria_update, name='categoria-update'),
    path('categorias/<int:pk>/deletar/', views.categoria_delete, name='categoria-delete'),
]