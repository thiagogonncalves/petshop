# Crediário da Casa (Fiado) – Guia de Uso e Testes

## Visão Geral

O módulo de Crediário da Casa permite vendas no fiado com parcelamento mensal. O cliente deve estar cadastrado e a venda avulsa é bloqueada.

## Backend – O que foi implementado

### Models
- **CreditAccount**: crediário vinculado a uma venda (OneToOne com Sale)
- **CreditInstallment**: parcelas do crediário (número, vencimento, valor, status)

### Sale – alterações
- Novo `payment_method`: `crediario` (Crediário da Casa)
- Novo `status`: `credit_open` (Crediário em aberto)

### Endpoints
- `POST /api/sales/sales/pdv/` – checkout com crediário (ver payload abaixo)
- `GET /api/credits/` – listar crediários (filtros: status, client_id, q, start, end)
- `GET /api/credits/{id}/` – detalhe do crediário com parcelas
- `POST /api/credits/installments/{id}/pay/` – dar baixa em parcela
- `GET /api/clients/{id}/credits/` – histórico de crediários do cliente

### Migrations
Execute: `python manage.py migrate sales`

## Frontend – O que foi implementado

### PDV (PdvSale.vue)
- Opção "Crediário da Casa" no checkout
- Ao selecionar crediário: obriga cliente (CPF), bloqueia venda avulsa
- Campos: entrada (opcional), número de parcelas (2–12), primeira data de vencimento
- Preview das parcelas no modal
- Redirecionamento para recibo após venda

### Menu Crediário
- Em aberto (`/credits?status=open`)
- Quitados (`/credits?status=settled`)
- Todos (`/credits`)

### Telas
- **CreditsList.vue** – lista de crediários com filtros
- **CreditDetail.vue** – detalhe do crediário e parcelas, botão Receber parcela
- **ClientCredits.vue** – histórico de crediários do cliente (link em Clientes)

## Como testar

### 1. Migrations
```bash
cd backend
python manage.py migrate sales
```

### 2. Criar venda no crediário (PDV)
1. Acesse **PDV** no menu
2. Adicione produtos ao carrinho
3. Clique em **Finalizar compra**
4. Selecione **Crediário da Casa**
5. Informe o CPF de um cliente cadastrado e clique em **Buscar cliente**
6. Preencha: entrada (opcional), parcelas, primeira data de vencimento
7. Confira o preview das parcelas
8. Clique em **Confirmar venda**

### 3. Listar crediários
1. Menu **Crediário** → **Em aberto** ou **Todos**
2. Use filtros: status, busca por cliente, período
3. Clique em **Ver** para ver o detalhe ou **Receber** para ir direto ao pagamento de parcelas

### 4. Dar baixa em parcela
1. Acesse o detalhe do crediário
2. Na tabela de parcelas, clique em **Receber** na parcela desejada
3. Confirme o pagamento no modal
4. A parcela passa para **Pago** e o status do crediário é atualizado

### 5. Histórico do cliente
1. Em **Clientes**, clique em **Crediário** na linha do cliente
2. Visualize todos os crediários daquele cliente

## Payload de exemplo – PDV com crediário

```json
{
  "client_cpf": "12345678901",
  "payment_method": "crediario",
  "is_walk_in": false,
  "down_payment": "0.00",
  "installments_count": 6,
  "first_due_date": "2026-02-28",
  "items": [
    {"product_id": 1, "quantity": 2, "unit_price": "19.90"},
    {"product_id": 5, "quantity": 1, "unit_price": "45.00"}
  ]
}
```

## Regras de negócio

- **Status da parcela**: PENDENTE → ATRASADA quando `hoje > due_date` (atualizado automaticamente ao listar)
- **Status do crediário**: ABERTO (há parcelas pendentes/atrasadas), QUITADO (todas pagas), CANCELADO
- **Cálculo**: total - entrada dividido em N parcelas; centavos ajustados na última parcela
- **Auditoria**: `created_by` na venda/crediário, `paid_by` no pagamento de parcela
