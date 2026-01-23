# Backend - Pet Shop Management System

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.10+
- PostgreSQL (opcional, pode usar SQLite para desenvolvimento)
- pip

### Instalação

1. **Criar ambiente virtual:**

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

2. **Instalar dependências:**

```bash
pip install -r requirements.txt
```

3. **Configurar variáveis de ambiente:**

Copie o arquivo `.env.example` (se existir) ou crie um `.env` na raiz do backend:

```env
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

4. **Executar migrações:**

```bash
python manage.py migrate
```

5. **Criar superusuário:**

```bash
python manage.py createsuperuser
```

6. **Criar diretório de logs:**

```bash
mkdir -p logs
```

7. **Iniciar servidor de desenvolvimento:**

```bash
python manage.py runserver
```

O servidor estará disponível em `http://localhost:8000`

## 📚 Endpoints Principais

- **Admin Django**: `http://localhost:8000/admin/`
- **API Swagger**: `http://localhost:8000/api/schema/swagger-ui/`
- **API ReDoc**: `http://localhost:8000/api/schema/redoc/`

## 🔧 Configuração do Banco de Dados

### SQLite (Padrão para desenvolvimento)

Não requer configuração adicional, funciona automaticamente.

### PostgreSQL (Produção)

1. Configure as variáveis de ambiente:

```env
USE_POSTGRES=True
DB_NAME=petshop_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

2. Crie o banco de dados:

```sql
CREATE DATABASE petshop_db;
```

3. Execute as migrações:

```bash
python manage.py migrate
```

## 👤 Criando Usuários

### Via Admin Django

Acesse `http://localhost:8000/admin/` e crie usuários com diferentes roles.

### Via Shell

```bash
python manage.py shell
```

```python
from apps.users.models import User, UserRole

# Criar admin
admin = User.objects.create_user(
    username='admin',
    email='admin@example.com',
    password='senha123',
    role=UserRole.ADMIN
)

# Criar gerente
manager = User.objects.create_user(
    username='gerente',
    email='gerente@example.com',
    password='senha123',
    role=UserRole.MANAGER
)

# Criar usuário
user = User.objects.create_user(
    username='usuario',
    email='usuario@example.com',
    password='senha123',
    role=UserRole.USER
)
```

## 🧪 Testes

```bash
python manage.py test
```

## 📦 Estrutura de Apps

- **users**: Autenticação e gestão de usuários
- **clients**: Gestão de clientes
- **pets**: Gestão de animais
- **products**: Produtos e controle de estoque
- **services**: Serviços oferecidos
- **scheduling**: Agendamentos
- **sales**: Vendas e faturamento
- **reports**: Relatórios
- **integrations**: Integrações externas (Mercado Pago, WhatsApp, Email)

## 🔐 Autenticação

O sistema usa JWT (JSON Web Tokens) para autenticação.

**Endpoint de login:**
```
POST /api/auth/users/login/
```

**Body:**
```json
{
  "username": "admin",
  "password": "senha123"
}
```

**Resposta:**
```json
{
  "access": "token...",
  "refresh": "refresh_token...",
  "user": {...}
}
```

Use o token no header:
```
Authorization: Bearer {access_token}
```
