from django.urls import path
from . import views

urlpatterns = [
    path('', views.movimentacao_list, name='movimentacao-list'),
    path('nova/', views.movimentacao_create, name='movimentacao-create'),
]
