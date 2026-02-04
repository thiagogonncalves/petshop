# Cobrança de Plano e Assinatura

## Visão geral

O sistema inclui cobrança de plano com:
- **Teste grátis de 7 dias** ao criar a empresa
- **Bloqueio em modo leitura** quando o trial expira (visualização permitida, criação/edição bloqueada)
- **Pagamento via Mercado Pago** (Checkout Pro)

## Configuração

### Variáveis de ambiente (.env)

```env
# Mercado Pago
MERCADOPAGO_ACCESS_TOKEN=seu_access_token
MERCADOPAGO_WEBHOOK_URL=https://seu-dominio.com/api/subscription/webhook/

# Frontend (para URLs de retorno do checkout)
FRONTEND_URL=https://seu-dominio.com
```

### Webhook no Mercado Pago

1. Acesse o [ painel de desenvolvedores do Mercado Pago](https://www.mercadopago.com.br/developers)
2. Configure a URL de notificação: `https://seu-dominio.com/api/subscription/webhook/`
3. O webhook recebe notificações de pagamento e atualiza o status da assinatura automaticamente

## Fluxo

1. **Criação da empresa (CompanySettings)** → Subscription criada com status `TRIAL`, 7 dias
2. **Durante o trial** → Todas as operações permitidas
3. **Após trial expirado** → Modo leitura (GET permitido, POST/PUT/DELETE bloqueado)
4. **Pagamento aprovado** → Status `ACTIVE`, período de 30 dias

## Endpoints

- `GET /api/subscription/status` — Status atual (autenticado)
- `POST /api/subscription/pay` — Gera link de pagamento Mercado Pago
- `POST /api/subscription/webhook` — Webhook Mercado Pago (AllowAny)

## Regras

- Usuário pode **visualizar tudo** sempre
- Só pode **criar/editar** com plano ativo ou trial dentro do prazo
- Rotas permitidas mesmo com assinatura expirada: login, token refresh, subscription/pay, webhook
- Dados **nunca são apagados** (models usam PROTECT, sem soft delete)
