#!/usr/bin/env python
"""
Script Python para resetar o banco de dados em desenvolvimento
"""
import os
import sys
import shutil

def reset_database():
    """Reset database by removing db.sqlite3 and migration files"""
    
    print("⚠️  ATENÇÃO: Este script irá deletar o banco de dados!")
    print("Todos os dados serão perdidos!")
    response = input("Deseja continuar? (s/N): ")
    
    if response.lower() != 's':
        print("Operação cancelada.")
        return
    
    # Remove database file
    db_file = 'db.sqlite3'
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"✅ Arquivo {db_file} removido.")
    
    # Remove migration files (except __init__.py)
    apps_dir = 'apps'
    if os.path.exists(apps_dir):
        for root, dirs, files in os.walk(apps_dir):
            if 'migrations' in dirs:
                migrations_dir = os.path.join(root, 'migrations')
                for file in os.listdir(migrations_dir):
                    if file != '__init__.py' and file.endswith(('.py', '.pyc')):
                        file_path = os.path.join(migrations_dir, file)
                        try:
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                            elif os.path.isdir(file_path):
                                shutil.rmtree(file_path)
                        except Exception as e:
                            print(f"⚠️  Erro ao remover {file_path}: {e}")
        
        print("✅ Arquivos de migração removidos.")
    
    print("\n🔄 Criando novas migrações...")
    os.system('python manage.py makemigrations')
    
    print("\n🔄 Aplicando migrações...")
    os.system('python manage.py migrate')
    
    print("\n✅ Banco de dados resetado com sucesso!")
    print("Agora você pode criar um superusuário com: python manage.py createsuperuser")

if __name__ == '__main__':
    reset_database()
