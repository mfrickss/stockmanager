"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.dashboard, name='dashboard'),
    path('produtos/', include('products.urls')),
    path('movimentacoes/', include('movements.urls')),
    path('login/',  core_views.login_view,  name='login'),
    path('registro/', core_views.register_view, name='register'),
    path('logout/', core_views.logout_view, name='logout'),
]