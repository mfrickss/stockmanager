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


def _login_jwt(client, username='testuser', password='testpass'):
    """Helper que faz login via JWT e retorna a response com cookies setados."""
    response = client.post('/login/', {
        'username': username,
        'password': password,
    })
    return response


# ==========================================
# Testes de Login JWT
# ==========================================

@pytest.mark.django_db
def test_login_gera_cookies_jwt(client, usuario):
    """Login bem-sucedido deve gerar cookies access_token e refresh_token."""
    response = _login_jwt(client)
    assert response.status_code == 302  # Redirect para dashboard
    assert 'access_token' in response.cookies
    assert 'refresh_token' in response.cookies
    # Cookies devem ser HttpOnly
    assert response.cookies['access_token']['httponly']
    assert response.cookies['refresh_token']['httponly']


@pytest.mark.django_db
def test_login_senha_incorreta(client, usuario):
    """Login com senha errada deve retornar a página de login com erro."""
    response = _login_jwt(client, password='senhaerrada')
    assert response.status_code == 200  # Renderiza o form com erro
    assert b'incorretos' in response.content


@pytest.mark.django_db
def test_login_redirect_next(client, usuario):
    """Login deve respeitar o parâmetro 'next' para redirecionamento."""
    response = client.post('/login/', {
        'username': 'testuser',
        'password': 'testpass',
        'next': '/produtos/',
    })
    assert response.status_code == 302
    assert response.url == '/produtos/'


# ==========================================
# Testes de Acesso Autenticado via JWT
# ==========================================

@pytest.mark.django_db
def test_dashboard_requer_login(client):
    """Dashboard sem token JWT deve redirecionar para login."""
    response = client.get('/')
    assert response.status_code == 302
    assert '/login/' in response.url


@pytest.mark.django_db
def test_dashboard_acessivel_com_jwt(client, usuario, categoria_e_produto):
    """Dashboard com cookie JWT válido deve retornar 200."""
    _login_jwt(client)
    response = client.get('/')
    assert response.status_code == 200
    assert b'Capital Imobilizado' in response.content


@pytest.mark.django_db
def test_dashboard_metricas(client, usuario, categoria_e_produto):
    """Métricas do dashboard devem estar corretas."""
    cat, prod = categoria_e_produto

    Movimentacao.objects.create(produto=prod, tipo='ENTRADA', quantidade=10, responsavel=usuario)
    Movimentacao.objects.create(produto=prod, tipo='SAIDA', quantidade=3, responsavel=usuario)

    _login_jwt(client)
    response = client.get('/?periodo=mes')

    assert response.status_code == 200
    assert response.context['qtd_entrada'] == 10
    assert response.context['qtd_saida'] == 3
    assert response.context['capital_imobilizado'] == 10000.00


# ==========================================
# Testes de Logout JWT
# ==========================================

@pytest.mark.django_db
def test_logout_remove_cookies(client, usuario):
    """Logout deve apagar os cookies JWT."""
    _login_jwt(client)
    response = client.get('/logout/')
    assert response.status_code == 302
    # Após logout, os cookies devem estar zerados
    assert response.cookies['access_token'].value == ''
    assert response.cookies['refresh_token'].value == ''


@pytest.mark.django_db
def test_logout_redireciona_para_login(client, usuario):
    """Após logout, deve redirecionar para a página de login."""
    _login_jwt(client)
    response = client.get('/logout/')
    assert response.status_code == 302
    assert '/login/' in response.url


@pytest.mark.django_db
def test_acesso_apos_logout_redireciona(client, usuario):
    """Após logout, tentar acessar página protegida deve redirecionar para login."""
    _login_jwt(client)
    client.get('/logout/')
    # Limpar cookies do client (simular navegador após delete_cookie)
    client.cookies.pop('access_token', None)
    client.cookies.pop('refresh_token', None)
    response = client.get('/')
    assert response.status_code == 302
    assert '/login/' in response.url
