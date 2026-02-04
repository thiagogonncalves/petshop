# Deploy em produção (Hostinger / Docker)

## Pré-requisitos

- Docker e Docker Compose instalados na VPS
- Domínio apontando para o IP da máquina (opcional, pode usar IP direto)
- Certificado SSL (Let's Encrypt) — recomendado para produção

## Estrutura

```
docker-compose.yml     → orquestra os serviços
backend/Dockerfile     → Django + Gunicorn
frontend/Dockerfile    → Vue build + Nginx (reverse proxy)
```

- **frontend** (porta 80): Nginx serve o Vue e faz proxy de `/api`, `/admin`, `/static`, `/media` para o backend
- **backend** (interno 8000): Django + Gunicorn
- **db**: PostgreSQL 16

## Passos para deploy

### 1. Clonar o repositório

```bash
git clone <seu-repositorio> petshop
cd petshop
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
nano .env
```

Edite e preencha:

- `SECRET_KEY`: gere com `python -c "import secrets; print(secrets.token_urlsafe(50))"`
- `DB_PASSWORD`: senha forte para o PostgreSQL
- `ALLOWED_HOSTS`: domínio ou IP (ex: `meupetshop.com.br,www.meupetshop.com.br`)
- `CSRF_TRUSTED_ORIGINS`: `https://meupetshop.com.br,https://www.meupetshop.com.br`
- `CORS_ALLOWED_ORIGINS`: mesmo que acima
- `FRONTEND_URL`: `https://meupetshop.com.br`
- `MERCADOPAGO_ACCESS_TOKEN`: token de produção do Mercado Pago
- `MERCADOPAGO_WEBHOOK_URL`: `https://meupetshop.com.br/api/subscription/webhook/`

### 3. Subir os containers

```bash
docker compose up -d --build
```

### 4. Criar superusuário (primeira vez)

```bash
docker compose exec backend python manage.py createsuperuser
```

### 5. (Opcional) Dados iniciais

```bash
docker compose exec backend python manage.py populate_data
```

## SSL com Let's Encrypt (Nginx na máquina)

Se quiser usar um Nginx na máquina (fora do Docker) para HTTPS:

1. Instale Certbot: `sudo apt install certbot python3-certbot-nginx`
2. Configure o Nginx como proxy reverso para `localhost:80` (porta do container frontend)
3. Rode: `sudo certbot --nginx -d meupetshop.com.br`

Ou use um proxy reverso como Traefik/Caddy em container para gerenciar SSL.

## Comandos úteis

```bash
# Ver logs
docker compose logs -f

# Reiniciar
docker compose restart

# Parar
docker compose down

# Atualizar e rebuildar
git pull
docker compose up -d --build
```

## Backup

```bash
# Backup do PostgreSQL
docker compose exec db pg_dump -U postgres petshop_db > backup_$(date +%Y%m%d).sql

# Restaurar
cat backup_20250101.sql | docker compose exec -T db psql -U postgres petshop_db
```

## Volumes

- `postgres_data`: dados do banco
- `media_data`: uploads (logos, fotos de pets, etc.)
