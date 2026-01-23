# Guia Rápido de Inicialização

## ⚡ Passos Rápidos para Começar

Execute os comandos na seguinte ordem:

### 1. Criar Migrações

```bash
python manage.py makemigrations
```

Este comando cria os arquivos de migração baseados nos models.

### 2. Aplicar Migrações

```bash
python manage.py migrate
```

Este comando cria todas as tabelas no banco de dados.

### 3. Criar Superusuário

```bash
python manage.py createsuperuser
```

Siga as instruções para criar o primeiro usuário administrador.

### 4. Iniciar Servidor

```bash
python manage.py runserver
```

## ⚠️ Troubleshooting

### Erro: "no such table: users_user"

**Causa**: Migrações não foram executadas.

**Solução**: Execute `python manage.py migrate` antes de criar usuários.

### Erro: "No migrations to create"

**Causa**: As migrações já foram criadas ou não há models.

**Solução**: Continue para o próximo passo (`python manage.py migrate`).

### Erro: "Module not found"

**Causa**: Ambiente virtual não está ativado.

**Solução**: 
```bash
source env/bin/activate  # Linux/Mac
# ou
env\Scripts\activate     # Windows
```

### Erro: "SECRET_KEY not set"

**Causa**: Arquivo `.env` não foi criado.

**Solução**: Crie um arquivo `.env` na pasta `backend/` com:

```env
SECRET_KEY=django-insecure-change-me-in-production-123456789
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## ✅ Verificação

Após executar os comandos, você deve conseguir:

1. ✅ Acessar `http://localhost:8000/admin/` e fazer login
2. ✅ Acessar `http://localhost:8000/api/schema/swagger-ui/` e ver a documentação da API
3. ✅ Fazer login via API em `/api/auth/users/login/`

## 🎯 Próximos Passos

1. Explore o admin em `/admin/`
2. Teste a API via Swagger em `/api/schema/swagger-ui/`
3. Configure o frontend (veja `../frontend/README.md`)
