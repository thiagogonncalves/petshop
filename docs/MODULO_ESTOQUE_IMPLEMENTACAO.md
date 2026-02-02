# Módulo de Estoque Inteligente – Plano e Implementação

## Resumo

Módulo de **estoque inteligente** implementado com:
- Controle por movimentações (entrada, saída, ajuste)
- Importação de NF-e (XML) e entrada de estoque
- Preço de venda calculado por margem % (com opção de preço manual)
- Integração backend (Django REST) e frontend (Vue 3)

---

## Backend

### 1. Products App

**Model Product (ajustes):**
- `gtin` (EAN, opcional)
- `profit_margin` (Decimal, % de lucro)
- `price_manually_set` (Boolean)
- Regra: `sale_price = cost_price * (1 + profit_margin/100)` exceto se `price_manually_set=True`
- Uso de `Decimal.quantize(0.01, ROUND_HALF_UP)`

**Model StockMovement:**
- Campos adicionados: `reference` (NF-e, venda, etc.), `cost_price` (nullable, para entrada)
- Método de classe: `StockMovement.get_stock_balance(product_id)` (saldo = soma das movimentações)

**Models Purchase e PurchaseItem:**
- `Purchase`: supplier_name, nfe_key (44), nfe_number, total_value, created_by
- `PurchaseItem`: purchase, product, quantity, unit_cost, total_cost

**Serviço:** `apps/products/services.py` – `calculate_sale_price(cost_price, profit_margin_percent)`

### 2. Integrations / NFe

**Estrutura:** `backend/apps/integrations/nfe/`

**Models:**
- `NFeImport`: access_key, xml_file, imported_at, status, supplier_name, nfe_number, imported_by
- `NFeImportItem`: nfe_import, product_name, quantity, unit, unit_cost, total_cost, gtin, product (FK opcional)

**Parser XML:** `apps/integrations/nfe/services/xml_parser.py`
- Lê XML da NF-e
- Extrai itens de `NFe > infNFe > det > prod`
- Mapeia: xProd, qCom (fallback qTrib), vUnCom (fallback vUnTrib), vProd, cEAN (ignora "SEM GTIN"), uCom/uTrib

**Fluxo de importação:**
1. POST XML → cria NFeImport + NFeImportItem (itens parseados)
2. Se `nfe_key` já existir → 409 Conflict (duplicada)
3. POST confirm com `items: [{ id, product_id?, profit_margin }]` → transaction.atomic(): cria Purchase, PurchaseItem, StockMovement (entrada), atualiza cost_price e sale_price do produto

### 3. API (Django REST)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/nfe/import-xml/` | Upload XML (multipart); retorna itens parseados |
| POST | `/api/nfe/{id}/confirm/` | Confirma entrada (body: `{ "items": [...] }`) |
| PATCH | `/api/products/{id}/pricing/` | Ajuste: `{ "profit_margin": 30 }` ou `{ "sale_price": 49.90, "price_manually_set": true }` |
| GET  | `/api/nfe/` | Lista importações |
| GET  | `/api/nfe/{id}/` | Detalhe importação com itens |
| GET  | `/api/products/purchases/` | Lista compras (read-only) |

---

## Frontend

### 1. Tela Importar NF-e (`views/ImportNFe.vue`)
- Upload de arquivo XML
- Lista de importações (chave, fornecedor, status, data)
- Modal “Confirmar entrada”: por item – vincular produto (ou criar novo), margem %, preço de venda calculado em tempo real; botão Confirmar entrada

### 2. Tela Produtos (`views/Products.vue`)
- Colunas: Código, Nome, Categoria, **Custo**, **Margem %**, **Preço**, Estoque, Status, Ações
- Modal produto: Preço de Custo, Margem de Lucro (%), Preço de Venda, checkbox “Preço definido manualmente”

### 3. Serviços e rotas
- `services/nfe.js`: importXml(file), list(), getById(id), confirm(importId, items)
- `services/products.js`: updatePricing(id, data)
- Rota `/nfe` e item de menu “Importar NF-e”

---

## Testes

- **apps/products/tests.py:** `calculate_sale_price`, Product com margem e preço manual
- **apps/integrations/nfe/tests.py:** parser XML (chave, fornecedor, itens, GTIN), importação duplicada (409)

Comando: `python manage.py test apps.products.tests apps.integrations.nfe.tests`

---

## Migrations

- `products.0003_stock_smart_pricing_purchase`: Product (gtin, profit_margin, price_manually_set), StockMovement (reference, cost_price), Purchase, PurchaseItem; dados: produtos existentes com `price_manually_set=True`
- `integrations.0001_nfe_import`: NFeImport, NFeImportItem

---

## Observações técnicas

- Confirmação da NF-e usa `transaction.atomic()`.
- Produtos existentes foram migrados com `price_manually_set=True` para manter o preço de venda atual.
- Parser suporta XML com e sem namespace (NFe/infNFe/det/prod).
- Código organizado com responsabilidades separadas (parser, pricing, views).
