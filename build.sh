#!/bin/bash
echo "Instalando dependências..."
python3 -m pip install -r requirements.txt

echo "Coletando arquivos estáticos..."
python3 manage.py collectstatic --noinput

echo "Rodando migrações..."
python3 manage.py migrate --noinput
