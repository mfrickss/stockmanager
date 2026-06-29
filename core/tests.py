import pytest
from django.contrib.auth.models import User
from products.models import Categoria, Produto
from movements.models import Movimentacao
from django.urls import reverse

@pytest.fixture
def usuario(db):
    return User.objects.create_user(username='testuser', password='testpass')

@pytest.fixture
def categoria_e_produto(db):
    cat = Categoria.objects.create(nome='Eletrônicos')
    prod = Produto.objects.create(
        nome='Smartphone', sku='SM-001', categoria=cat, 
        preco=2000.00, quantidade_estoque=5
    )
    return cat, prod

@pytest.mark.django_db
def test_dashboard_requer_login(client):
    response = client.get('/')
    assert response.status_code == 302
    assert '/login/' in response.url

@pytest.mark.django_db
def test_dashboard_carrega_com_sucesso(client, usuario, categoria_e_produto):
    client.login(username='testuser', password='testpass')
    response = client.get('/')
    assert response.status_code == 200
    # O produto em estoque crítico (5) deve aparecer na tela
    assert b'Smartphone' in response.content
    assert b'Capital Imobilizado' in response.content

@pytest.mark.django_db
def test_dashboard_metricas(client, usuario, categoria_e_produto):
    cat, prod = categoria_e_produto
    
    # Criar movimentações
    Movimentacao.objects.create(produto=prod, tipo='ENTRADA', quantidade=10, responsavel=usuario)
    Movimentacao.objects.create(produto=prod, tipo='SAIDA', quantidade=3, responsavel=usuario)
    
    client.login(username='testuser', password='testpass')
    response = client.get('/?periodo=mes')
    
    assert response.status_code == 200
    # Validações simples de contexto para garantir que os cálculos funcionaram
    # 10 entradas, 3 saídas
    assert response.context['qtd_entrada'] == 10
    assert response.context['qtd_saida'] == 3
    # Capital imobilizado: 5 estoque * 2000.00 preco = 10000.00
    assert response.context['capital_imobilizado'] == 10000.00
