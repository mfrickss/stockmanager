import pytest
from django.contrib.auth.models import User
from .models import Categoria, Produto

@pytest.fixture
def usuario(db):
    return User.objects.create_user(username='testuser', password='testpass')

@pytest.fixture
def categoria(db):
    return Categoria.objects.create(nome='Eletrônicos', descricao='Produtos de tecnologia')

@pytest.mark.django_db
def test_criar_produto_model(categoria):
    produto = Produto.objects.create(
        nome='Lâmpada LED', sku='LED-001',
        categoria=categoria, preco=15.90, quantidade_estoque=100
    )
    assert produto.pk is not None
    assert str(produto) == "Lâmpada LED (LED-001)"
    assert produto.categoria.nome == 'Eletrônicos'

@pytest.mark.django_db
def test_lista_produtos_requer_login(client):
    response = client.get('/')
    assert response.status_code == 302  # Redirects to login
    assert '/login/' in response.url

@pytest.mark.django_db
def test_lista_produtos_autenticado(client, usuario, categoria):
    Produto.objects.create(nome='Monitor', sku='MON-001', categoria=categoria, preco=1200.00, quantidade_estoque=10)
    
    client.login(username='testuser', password='testpass')
    response = client.get('/')
    
    assert response.status_code == 200
    assert b'Monitor' in response.content