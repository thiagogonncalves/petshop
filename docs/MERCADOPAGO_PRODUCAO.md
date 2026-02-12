# Mercado Pago - Configuração para Produção

## Análise do estado atual

### O que está configurado
- Token de acesso (`MERCADOPAGO_ACCESS_TOKEN`) definido
- Webhook handler implementado em `/api/subscription/webhook/`
- Checkout Pro com `notification_url` na preferência
- Fluxo: trial → pagamento → ACTIVE por 30 dias

### Problemas identificados no `.env`

| Variável | Atual | Produção |
|----------|-------|----------|
| `MERCADOPAGO_WEBHOOK_URL` | `https://acetated-minta-fastidiously.ngrok-free.dev/...` (ngrok - dev) | `https://begpet.petshow.online/api/subscription/webhook/` |
| `FRONTEND_URL` | Duplicado: linha 16 = begpet; linha 23 = localhost (sobrescreve) | `https://begpet.petshow.online` |
| `SECURE_SSL_REDIRECT` | false | true (quando usar HTTPS) |

---

## Checklist para produção

### 1. Ajustar variáveis no `.env`

```env
# Mercado Pago (assinatura)
MERCADOPAGO_ACCESS_TOKEN=APP_USR-seu-token-producao
MERCADOPAGO_WEBHOOK_URL=https://begpet.petshow.online/api/subscription/webhook/

# Domínio (remover duplicata de FRONTEND_URL)
FRONTEND_URL=https://begpet.petshow.online

# SSL (ativar em produção)
SECURE_SSL_REDIRECT=true
```

### 2. Credenciais do Mercado Pago

1. Acesse [Suas integrações - Mercado Pago](https://www.mercadopago.com.br/developers/panel/app)
2. Selecione sua aplicação
3. Em **Credenciais** → use as credenciais de **Produção** (não Teste)
4. O token de produção tem formato `APP_USR-...` (Access Token)
5. Copie o token e coloque em `MERCADOPAGO_ACCESS_TOKEN`

### 3. Webhook no painel do Mercado Pago

**Opção A – Via Suas integrações (recomendado):**
1. Acesse [Suas integrações](https://www.mercadopago.com.br/developers/panel/app)
2. Webhooks → Configurar notificações
3. **URL modo produção:** `https://begpet.petshow.online/api/subscription/webhook/`
4. Evento: **Pagamentos** (`payment`)
5. Salvar (gera assinatura secreta para validação)

**Opção B – Via notification_url (já em uso):**  
O sistema já envia `notification_url` na preferência. O Mercado Pago usa essa URL e ela tem prioridade sobre a do painel. Verifique se a URL está correta na preferência.

### 4. Requisitos técnicos

- **HTTPS** – O webhook deve ser acessível via HTTPS
- **Domínio público** – O Mercado Pago precisa alcançar a URL
- **Firewall** – Porta 443 liberada para o Mercado Pago

### 5. Validação da assinatura do webhook (implementado)

O webhook valida o header `x-signature` quando `MERCADOPAGO_WEBHOOK_SECRET` está configurado:

1. Acesse [Suas integrações](https://www.mercadopago.com.br/developers/panel/app) → Webhooks → **Reveal** (revelar assinatura secreta)
2. Copie o secret e adicione no `.env`:
   ```env
   MERCADOPAGO_WEBHOOK_SECRET=seu_secret_aqui
   ```

Sem o secret configurado, o webhook continua funcionando (compatibilidade). Com o secret, requisições com assinatura inválida retornam 401.

**Nota:** Quando a URL é configurada via `notification_url` (na preferência), o Mercado Pago pode não enviar `x-signature`. Nesse caso, configure o webhook também pelo painel (Opção A) para receber a assinatura.

### 6. Tratamento do tipo de notificação

O webhook pode receber `type: "payment"` ou `type: "preference"`. O código atual assume `payment`. Quando `type` for `preference`, `data.id` é o ID da preferência, não do pagamento. Filtrar apenas `type == "payment"` evita erros.

---

## Resumo – o que fazer agora

1. Alterar `.env`:
   - `MERCADOPAGO_WEBHOOK_URL=https://begpet.petshow.online/api/subscription/webhook/`
   - `FRONTEND_URL=https://begpet.petshow.online` (apenas uma vez)
   - `SECURE_SSL_REDIRECT=true` (se usar HTTPS)

2. Conferir token de produção no painel do Mercado Pago.

3. Garantir que a aplicação esteja em HTTPS em produção.

4. Testar: gerar um pagamento de teste em produção e confirmar se o webhook é chamado e a assinatura é atualizada.

5. **(Recomendado)** Configurar `MERCADOPAGO_WEBHOOK_SECRET` para validar a origem das notificações.
