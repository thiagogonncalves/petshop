#!/bin/bash
# Script para resetar o banco de dados em desenvolvimento

echo "⚠️  ATENÇÃO: Este script irá deletar o banco de dados!"
echo "Todos os dados serão perdidos!"
read -p "Deseja continuar? (s/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]
then
    echo "Operação cancelada."
    exit 1
fi

echo "Removendo banco de dados..."
rm -f db.sqlite3

echo "Removendo migrações (exceto __init__.py)..."
find apps/ -path "*/migrations/*.py" -not -name "__init__.py" -delete
find apps/ -path "*/migrations/*.pyc" -delete

echo "Criando novas migrações..."
python manage.py makemigrations

echo "Aplicando migrações..."
python manage.py migrate

echo "✅ Banco de dados resetado com sucesso!"
echo "Agora você pode criar um superusuário com: python manage.py createsuperuser"
