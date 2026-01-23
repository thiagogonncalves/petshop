# Guia de Instalação Completo - Pet Shop Management System

## 📋 Pré-requisitos

### Backend
- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)
- PostgreSQL (opcional - pode usar SQLite para desenvolvimento)
- Git

### Frontend
- Node.js 16 ou superior
- npm ou yarn

## 🚀 Instalação Passo a Passo

### 1. Clone o Repositório

```bash
git clone <repository-url>
cd petshop
```

### 2. Configuração do Backend

#### 2.1. Criar Ambiente Virtual

```bash
cd backend
python -m venv venv
```

**No Windows:**
```cmd
cd backend
python -m venv venv
venv\Scripts\activate
```

**No Linux/Mac:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
```

#### 2.2. Instalar Dependências

```bash
pip install -r requirements.txt
```

#### 2.3. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na pasta `backend/`:

```env
SECRET_KEY=django-insecure-change-me-in-production-123456789
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Opcional: Para usar PostgreSQL
USE_POSTGRES=False
DB_NAME=petshop_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

#### 2.4. Executar Migrações

```bash
python manage.py migrate
```

#### 2.5. Criar Superusuário

```bash
python manage.py createsuperuser
```

Siga as instruções para criar o primeiro usuário administrador.

#### 2.6. Criar Diretório de Logs

```bash
mkdir -p logs
```

**No Windows:**
```cmd
mkdir logs
```

#### 2.7. Iniciar Servidor

```bash
python manage.py runserver
```

O backend estará disponível em: `http://localhost:8000`

**Endpoints importantes:**
- Admin: `http://localhost:8000/admin/`
- API Swagger: `http://localhost:8000/api/schema/swagger-ui/`
- API ReDoc: `http://localhost:8000/api/schema/redoc/`

### 3. Configuração do Frontend

#### 3.1. Instalar Dependências

Em um novo terminal (mantenha o backend rodando):

```bash
cd frontend
npm install
```

#### 3.2. Iniciar Servidor de Desenvolvimento

```bash
npm run dev
```

O frontend estará disponível em: `http://localhost:5173`

## ✅ Verificação da Instalação

### Backend

1. Acesse `http://localhost:8000/admin/`
2. Faça login com o superusuário criado
3. Verifique se todos os apps aparecem no admin

### Frontend

1. Acesse `http://localhost:5173`
2. Você verá a tela de login
3. Use as credenciais do superusuário para entrar

### API

1. Acesse `http://localhost:8000/api/schema/swagger-ui/`
2. Teste o endpoint de login:
   - POST `/api/auth/users/login/`
   - Body: `{"username": "seu_usuario", "password": "sua_senha"}`

## 👥 Criando Usuários de Teste

### Via Admin Django

1. Acesse `http://localhost:8000/admin/`
2. Vá em "Usuários" > "Adicionar"
3. Crie usuários com diferentes roles:
   - **admin**: Acesso total
   - **manager**: Gerente
   - **user**: Usuário comum

### Via Shell Python

```bash
cd backend
python manage.py shell
```

```python
from apps.users.models import User, UserRole

# Admin
User.objects.create_user(
    username='admin',
    email='admin@petshop.com',
    password='admin123',
    role=UserRole.ADMIN
)

# Gerente
User.objects.create_user(
    username='gerente',
    email='gerente@petshop.com',
    password='gerente123',
    role=UserRole.MANAGER
)

# Usuário
User.objects.create_user(
    username='usuario',
    email='usuario@petshop.com',
    password='usuario123',
    role=UserRole.USER
)
```

## 🗄️ Banco de Dados

### SQLite (Padrão - Desenvolvimento)

O SQLite é usado por padrão e não requer configuração adicional. O arquivo `db.sqlite3` será criado automaticamente.

### PostgreSQL (Recomendado para Produção)

1. Instale e configure PostgreSQL
2. Crie o banco de dados:

```sql
CREATE DATABASE petshop_db;
CREATE USER petshop_user WITH PASSWORD 'sua_senha';
GRANT ALL PRIVILEGES ON DATABASE petshop_db TO petshop_user;
```

3. Configure o `.env`:

```env
USE_POSTGRES=True
DB_NAME=petshop_db
DB_USER=petshop_user
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
```

4. Execute as migrações:

```bash
python manage.py migrate
```

## 🔧 Resolução de Problemas

### Erro: "Module not found"

```bash
# Certifique-se de estar no ambiente virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstale as dependências
pip install -r requirements.txt
```

### Erro: "Port already in use"

**Backend (porta 8000):**
```bash
python manage.py runserver 8001
```

**Frontend (porta 5173):**
Edite `vite.config.js` e mude a porta.

### Erro de CORS

Certifique-se de que o backend está configurado para aceitar requisições do frontend. O arquivo `core/settings/base.py` já tem CORS configurado para desenvolvimento.

### Erro ao criar usuário

```bash
python manage.py createsuperuser
```

Se ainda houver problemas, crie via shell:

```bash
python manage.py shell
```

```python
from apps.users.models import User
User.objects.create_superuser('admin', 'admin@example.com', 'senha123')
```

## 📚 Próximos Passos

1. **Explorar a API**: Acesse `http://localhost:8000/api/schema/swagger-ui/`
2. **Criar dados de teste**: Use o admin para criar clientes, produtos, etc.
3. **Testar o frontend**: Faça login e explore as funcionalidades
4. **Ler documentação**: Consulte `ARCHITECTURE.md` e `API_EXAMPLES.md`

## 🚀 Produção

Para deploy em produção:

1. Configure `DEBUG=False` no `.env`
2. Configure uma `SECRET_KEY` segura
3. Configure `ALLOWED_HOSTS` com seu domínio
4. Use PostgreSQL como banco de dados
5. Configure servidor web (Nginx + Gunicorn)
6. Configure HTTPS
7. Configure variáveis de ambiente de forma segura
8. Execute `npm run build` no frontend e sirva os arquivos estáticos

## 📞 Suporte

Para mais informações, consulte:
- `README.md` - Visão geral
- `ARCHITECTURE.md` - Arquitetura do sistema
- `API_EXAMPLES.md` - Exemplos de uso da API
