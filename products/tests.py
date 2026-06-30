import pytest
from django.contrib.auth.models import User
from .models import Categoria, Produto


@pytest.fixture
def usuario(db):
    return User.objects.create_user(username='testuser', password='testpass')


@pytest.fixture
def categoria(db):
    return Categoria.objects.create(nome='Eletrônicos', descricao='Produtos de tecnologia')


def _login_jwt(client):
    """Helper para autenticar via JWT."""
    client.post('/login/', {'username': 'testuser', 'password': 'testpass'})


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
    response = client.get('/produtos/')
    assert response.status_code == 302  # Redirects to login
    assert '/login/' in response.url


@pytest.mark.django_db
def test_lista_produtos_autenticado(client, usuario, categoria):
    Produto.objects.create(nome='Monitor', sku='MON-001', categoria=categoria, preco=1200.00, quantidade_estoque=10)

    _login_jwt(client)
    response = client.get('/produtos/')

    assert response.status_code == 200
    assert b'Monitor' in response.content


@pytest.mark.django_db
def test_categoria_create_ajax(client, usuario):
    _login_jwt(client)

    # Test valid creation
    response = client.post('/produtos/categorias/ajax-nova/', {'nome': 'Nova Categoria AJAX'}, content_type='application/json')
    assert response.status_code == 200
    assert response.json()['success'] is True
    assert Categoria.objects.filter(nome='Nova Categoria AJAX').exists()

    # Test duplicate creation
    response2 = client.post('/produtos/categorias/ajax-nova/', {'nome': 'Nova Categoria AJAX'}, content_type='application/json')
    assert response2.status_code == 200
    assert response2.json()['success'] is False


@pytest.mark.django_db
def test_produto_stock_adjust_ajax(client, usuario, categoria):
    prod = Produto.objects.create(nome='Mouse', sku='MOU-001', categoria=categoria, preco=50.00, quantidade_estoque=10)
    _login_jwt(client)

    # Adicionar estoque
    response = client.post(f'/produtos/{prod.id}/estoque/ajax/', {'action': 'increase'}, content_type='application/json')
    assert response.status_code == 200
    prod.refresh_from_db()
    assert prod.quantidade_estoque == 11

    # Remover estoque
    response2 = client.post(f'/produtos/{prod.id}/estoque/ajax/', {'action': 'decrease'}, content_type='application/json')
    assert response2.status_code == 200
    prod.refresh_from_db()
    assert prod.quantidade_estoque == 10

    # Test invalid action
    response3 = client.post(f'/produtos/{prod.id}/estoque/ajax/', {'action': 'invalid'}, content_type='application/json')
    assert response3.status_code == 200
    assert response3.json()['success'] is False