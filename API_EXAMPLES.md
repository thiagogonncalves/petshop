# Exemplos de Uso da API

## 🔐 Autenticação

### Login

```bash
POST /api/auth/users/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "senha123"
}
```

**Resposta:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "role_display": "Administrador"
  }
}
```

### Usar Token

```bash
GET /api/auth/users/me/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## 👥 Clientes

### Listar Clientes

```bash
GET /api/clients/
Authorization: Bearer {token}
```

**Resposta:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "João Silva",
      "document_type": "cpf",
      "document": "12345678901",
      "phone": "11999999999",
      "email": "joao@example.com",
      "street": "Rua Exemplo",
      "number": "123",
      "neighborhood": "Centro",
      "city": "São Paulo",
      "state": "SP",
      "zip_code": "01000-000",
      "is_active": true,
      "created_at": "2024-01-01T10:00:00Z"
    }
  ]
}
```

### Criar Cliente

```bash
POST /api/clients/
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Maria Santos",
  "document_type": "cpf",
  "document": "98765432100",
  "phone": "11988888888",
  "email": "maria@example.com",
  "street": "Av. Principal",
  "number": "456",
  "neighborhood": "Jardim",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "02000-000"
}
```

### Obter Animais de um Cliente

```bash
GET /api/clients/{id}/pets/
Authorization: Bearer {token}
```

## 🐾 Animais

### Listar Animais

```bash
GET /api/pets/
Authorization: Bearer {token}
```

### Criar Animal

```bash
POST /api/pets/
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Rex",
  "species": "dog",
  "breed": "Labrador",
  "birth_date": "2020-05-15",
  "weight": 25.5,
  "sex": "male",
  "color": "Amarelo",
  "client": 1,
  "observations": "Muito dócil"
}
```

## 📦 Produtos

### Listar Produtos

```bash
GET /api/products/products/
Authorization: Bearer {token}
```

### Criar Produto

```bash
POST /api/products/products/
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Ração Premium",
  "description": "Ração para cães adultos",
  "category": 1,
  "barcode": "7891234567890",
  "cost_price": 50.00,
  "sale_price": 80.00,
  "stock_quantity": 100,
  "min_stock": 20,
  "unit": "kg"
}
```

### Produtos com Estoque Baixo

```bash
GET /api/products/products/low_stock/
Authorization: Bearer {token}
```

### Movimentação de Estoque

```bash
POST /api/products/stock-movements/
Authorization: Bearer {token}
Content-Type: application/json

{
  "product": 1,
  "movement_type": "entry",
  "quantity": 50,
  "observation": "Entrada de estoque"
}
```

## 🛎️ Serviços

### Listar Serviços

```bash
GET /api/services/
Authorization: Bearer {token}
```

### Criar Serviço

```bash
POST /api/services/
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Banho e Tosa",
  "description": "Banho completo com tosa",
  "price": 80.00,
  "duration_minutes": 120
}
```

## 📅 Agendamentos

### Listar Agendamentos

```bash
GET /api/scheduling/
Authorization: Bearer {token}
```

### Criar Agendamento

```bash
POST /api/scheduling/
Authorization: Bearer {token}
Content-Type: application/json

{
  "client": 1,
  "pet": 1,
  "service": 1,
  "scheduled_date": "2024-01-15T14:00:00Z",
  "observations": "Primeira vez"
}
```

### Agendamentos de Hoje

```bash
GET /api/scheduling/today/
Authorization: Bearer {token}
```

### Completar Agendamento

```bash
POST /api/scheduling/{id}/complete/
Authorization: Bearer {token}
```

## 💰 Vendas

### Criar Venda

```bash
POST /api/sales/sales/
Authorization: Bearer {token}
Content-Type: application/json

{
  "client": 1,
  "items": [
    {
      "item_type": "product",
      "product": 1,
      "quantity": 2,
      "unit_price": 80.00
    },
    {
      "item_type": "service",
      "service": 1,
      "quantity": 1,
      "unit_price": 80.00
    }
  ],
  "discount": 10.00,
  "payment_method": "pix",
  "status": "paid"
}
```

### Listar Vendas

```bash
GET /api/sales/sales/?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {token}
```

### Completar Pagamento

```bash
POST /api/sales/sales/{id}/complete_payment/
Authorization: Bearer {token}
```

### Gerar Recibo

```bash
POST /api/sales/sales/{id}/generate_receipt/
Authorization: Bearer {token}
```

## 📊 Relatórios

### Dashboard

```bash
GET /api/reports/dashboard/
Authorization: Bearer {token}
```

**Resposta:**
```json
{
  "sales": {
    "today": {
      "total": 1500.00,
      "count": 5
    },
    "this_month": {
      "total": 45000.00,
      "count": 150
    }
  },
  "appointments": {
    "today": 8,
    "upcoming": 15
  },
  "inventory": {
    "low_stock_count": 3
  },
  "clients": {
    "total": 250,
    "total_pets": 320
  }
}
```

### Resumo de Vendas

```bash
GET /api/reports/sales_summary/?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {token}
```

### Status do Estoque

```bash
GET /api/reports/inventory_status/
Authorization: Bearer {token}
```

### Top Produtos

```bash
GET /api/reports/top_products/?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {token}
```

## 🔗 Integrações

### Processar Pagamento Mercado Pago

```bash
POST /api/integrations/mercado_pago_payment/
Authorization: Bearer {token}
Content-Type: application/json

{
  "sale_id": 1,
  "payment_method_id": "pix"
}
```

### Enviar WhatsApp

```bash
POST /api/integrations/send_whatsapp/
Authorization: Bearer {token}
Content-Type: application/json

{
  "phone_number": "11999999999",
  "message": "Olá! Seu agendamento está confirmado."
}
```

### Confirmar Agendamento via WhatsApp

```bash
POST /api/integrations/send_appointment_confirmation/
Authorization: Bearer {token}
Content-Type: application/json

{
  "appointment_id": 1
}
```

### Enviar Recibo por E-mail

```bash
POST /api/integrations/send_receipt_email/
Authorization: Bearer {token}
Content-Type: application/json

{
  "receipt_id": 1
}
```

## 📊 Relatórios (módulo Reports)

Todos os endpoints de relatórios exigem autenticação (`Authorization: Bearer {token}`). Datas no formato `YYYY-MM-DD`. Por padrão, vendas consideradas são apenas **pagas** (`status=paid`); use `include_cancelled=true` ou `status=` para incluir canceladas/outros.

### Vendedores (filtros)

```bash
GET /api/reports/sellers/
```

Retorna lista de usuários que têm vendas (para dropdown de filtro).

### Dashboard (KPIs)

```bash
GET /api/reports/dashboard/?start=2025-01-01&end=2025-01-27&user_id=&payment_method=&status=paid
```

**Resposta:** `total_sales`, `total_revenue`, `ticket_avg`, `total_items_sold`, `estimated_profit`, `sales_by_day`, `sales_by_payment_method`, `top_5_products`, `top_5_clients`, `period`.

### Relatório de vendas (lista paginada)

```bash
GET /api/reports/sales/?start=2025-01-01&end=2025-01-27&page=1&page_size=20&user_id=&client_id=&status=&q=&include_cancelled=false
```

**Resposta:** `{ count, next, previous, results: [ { id, sale_date, created_by_name, client_name, total, payment_method, status, ... } ] }`.

### Produtos vendidos

```bash
GET /api/reports/products-sold/?start=2025-01-01&end=2025-01-27&category_id=&order=revenue&limit=100
```

`order`: `revenue` | `qty` | `profit`. **Resposta:** `results`: lista com `product_id`, `name`, `quantity_total`, `revenue_total`, `avg_price`, `estimated_profit`, `share_percent`.

### Ranking de vendedores

```bash
GET /api/reports/sales-ranking/?start=2025-01-01&end=2025-01-27&order=revenue&limit=20
```

`order`: `revenue` | `count` | `items`. **Resposta:** `results`: lista com `user_id`, `name`, `total_sales`, `items_sold`, `revenue`, `ticket_avg`, `cancellation_rate`.

### Estoque baixo

```bash
GET /api/reports/low-stock/?threshold=5
```

Sem `threshold`: usa estoque mínimo do produto. **Resposta:** `results`: produto, saldo, mínimo, sugestão de reposição.

### Top clientes

```bash
GET /api/reports/top-clients/?start=2025-01-01&end=2025-01-27&order=revenue&limit=20
```

### Exportação CSV

```bash
GET /api/reports/sales/export.csv?start=2025-01-01&end=2025-01-27
GET /api/reports/products-sold/export.csv?start=2025-01-01&end=2025-01-27&order=revenue
```

Retornam arquivo CSV com `Content-Disposition: attachment; filename="..."`.

---

## 📝 Filtros e Busca

### Filtros Comuns

Muitos endpoints suportam filtros via query parameters:

```bash
# Clientes ativos
GET /api/clients/?is_active=true

# Vendas por período
GET /api/sales/sales/?start_date=2024-01-01&end_date=2024-01-31

# Agendamentos de um cliente
GET /api/scheduling/?client=1

# Produtos por categoria
GET /api/products/products/?category=1
```

### Busca

Endpoints com busca por texto:

```bash
# Buscar clientes
GET /api/clients/?search=João

# Buscar produtos
GET /api/products/products/?search=ração
```

## 🚫 Tratamento de Erros

### Resposta de Erro Padrão

```json
{
  "error": true,
  "message": "Erro na requisição",
  "details": {
    "field_name": ["Mensagem de erro específica"]
  },
  "status_code": 400
}
```

### Exemplos

**400 Bad Request:**
```json
{
  "error": true,
  "message": "Erro na requisição",
  "details": {
    "quantity": ["Quantidade maior que estoque disponível"]
  },
  "status_code": 400
}
```

**401 Unauthorized:**
```json
{
  "detail": "Token de autenticação não fornecido ou inválido."
}
```

**404 Not Found:**
```json
{
  "error": true,
  "message": "Erro na requisição",
  "details": {
    "detail": "Não encontrado."
  },
  "status_code": 404
}
```
