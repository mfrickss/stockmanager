# StockManager Premium

Um sistema de gestão de estoque completo, focado em alta performance. Desenvolvido com **Django 5** e **MySQL**.

## Tecnologias Utilizadas

- **Backend:** Python 3.11+ e Django 5.
- **Banco de Dados:** MySQL (configurado via Django ORM).
- **Frontend:** Vanilla CSS Moderno, HTML5.
- **Testes:** `pytest` e `pytest-django`.

## Funcionalidades

- **Dashboard Financeiro & Gerencial:** Tela principal com capital imobilizado, alertas de estoque crítico (≤10), e rankings (Top 5 Produtos e Top 5 Categorias) com filtro de tempo.
- **Movimentações de Estoque:** Histórico automatizado de todas as entradas e saídas (compras e vendas) em tempo real.
- **Gestão Ágil via AJAX:**
  - Adição rápida de quantidade no estoque diretamente da listagem sem recarregar a página.
  - Criação dinâmica de Categorias a partir do formulário de Produto através de modais interativos.
- **CRUD Completo:** Criação, leitura, atualização e exclusão segura de produtos e categorias.
- **Autenticação Segura:** Proteção total de rotas; redirecionamento automático para tela de login customizada.
- **Painel Administrativo:** Django Admin integrado para gestão avançada.
- **Interface Premium:**
  - Design system consistente (Slate + Indigo/Purple).
  - Componentes de vidro (Glassmorphism).
  - Micro-interações nativas e ícones (Phosphor Icons).

## Como rodar o projeto localmente

### 1. Clonar o Repositório e Configurar Ambiente

```bash
git clone https://github.com/mfrickss/stockmanager.git
cd stockmanager
python -m venv .venv
.venv\Scripts\activate  # Windows
```

### 2. Instalar Dependências

```bash
pip install django mysqlclient pytest-django
```

### 3. Banco de Dados (MySQL)

Crie um banco de dados no MySQL local:

```sql
CREATE DATABASE stockmanager_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Abra o arquivo `core/settings.py` e configure a sua senha do `root`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'stockmanager_db',
        'USER': 'root',
        'PASSWORD': 'SUA_SENHA_AQUI',
        'HOST': 'localhost',
        'PORT': '3306'
    }
}
```

### 4. Rodar Migrações e Servidor

```bash
python manage.py migrate
python manage.py createsuperuser  # Crie seu usuário de acesso
python manage.py runserver
```

Acesse **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** para ver a aplicação rodando!

## Rodando os Testes Automatizados

O sistema conta com testes de regressão para autenticação e integridade do banco de dados. Para rodá-los:

```bash
pytest --tb=short
```

---

_Desenvolvido por Ricardo Camargo._
