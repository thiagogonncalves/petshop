# Arquitetura do Sistema Pet Shop

## 📐 Visão Geral

Sistema desenvolvido seguindo padrões de arquitetura modular, separação de responsabilidades e preparado para escalabilidade.

## 🏗️ Estrutura do Backend

### Organização Modular

O backend está organizado em apps Django independentes, cada um com responsabilidade específica:

```
backend/
├── core/                    # Configurações centrais
│   ├── settings/           # Configurações por ambiente
│   ├── urls.py             # URLs principais
│   └── exceptions.py       # Tratamento global de erros
├── apps/
│   ├── users/              # Autenticação e usuários (RBAC)
│   ├── clients/            # Gestão de clientes
│   ├── pets/               # Gestão de animais
│   ├── products/           # Produtos e estoque
│   ├── services/           # Serviços oferecidos
│   ├── scheduling/         # Agendamentos
│   ├── sales/              # Vendas e faturamento
│   ├── reports/            # Relatórios
│   └── integrations/       # Integrações externas
```

### Padrão de Cada App

Cada app segue uma estrutura consistente:

```
app_name/
├── models.py          # Modelos de dados
├── serializers.py     # Serializers DRF
├── views.py           # ViewSets e views
├── urls.py            # Rotas da API
├── admin.py           # Configuração do admin Django
├── permissions.py     # Permissões customizadas (quando necessário)
└── apps.py            # Configuração do app
```

## 🔐 Sistema de Autenticação

### JWT (JSON Web Tokens)

- **Biblioteca**: `djangorestframework-simplejwt`
- **Tokens**: Access Token (1h) + Refresh Token (7 dias)
- **Rotação**: Refresh tokens são rotacionados automaticamente

### RBAC (Role-Based Access Control)

Três níveis de permissão:

1. **Administrador** (`admin`)
   - Acesso total ao sistema
   - Gerenciar usuários
   - Configurações gerais

2. **Gerente** (`manager`)
   - Gerenciar usuários (exceto admins)
   - Relatórios completos
   - Visualizar vendas e estoque

3. **Usuário** (`user`)
   - Operações básicas (vendas, cadastros)
   - Relatórios limitados

### Permissões Customizadas

Criadas em `apps/users/permissions.py`:
- `IsAdmin`: Apenas administradores
- `IsAdminOrManager`: Admin ou Gerente
- `CanManageUsers`: Gerenciar usuários
- `CanViewReports`: Visualizar relatórios

## 📊 Models e Relacionamentos

### Principais Entidades

```
User (Custom)
├── Role (admin/manager/user)
└── Permissions

Client
├── Document (CPF/CNPJ)
└── Address

Pet
├── Client (ForeignKey)
└── Species/Breed/Weight

Product
├── Category (ForeignKey)
├── Pricing (cost/sale)
└── Inventory (stock/min_stock)

StockMovement
├── Product (ForeignKey)
├── Type (entry/exit/adjustment)
└── Quantity tracking

Service
└── Price & Duration

Appointment
├── Client (ForeignKey)
├── Pet (ForeignKey)
├── Service (ForeignKey)
└── Scheduled Date/Time

Sale
├── Client (ForeignKey)
├── Items (SaleItem)
├── Payment Method
└── Status

SaleItem
├── Sale (ForeignKey)
├── Product OR Service
└── Quantity/Price
```

## 🔄 API REST

### Padrão RESTful

Todos os endpoints seguem convenções REST:

- `GET /api/resource/` - Listar
- `POST /api/resource/` - Criar
- `GET /api/resource/{id}/` - Detalhar
- `PATCH /api/resource/{id}/` - Atualizar (parcial)
- `PUT /api/resource/{id}/` - Atualizar (completo)
- `DELETE /api/resource/{id}/` - Deletar

### ViewSets

Utilizamos ViewSets do DRF para facilitar a criação de CRUD completo:

```python
class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
```

### Actions Customizadas

Actions adicionais usando decorator `@action`:

```python
@action(detail=True, methods=['post'])
def complete_payment(self, request, pk=None):
    # Lógica customizada
    pass
```

## 📝 Serializers

### Estrutura

- Serializers base para CRUD
- Serializers específicos para criação (`CreateSerializer`)
- Serializers com métodos customizados para cálculos

### Serialização de Relacionamentos

Utilizamos `source` para incluir dados relacionados:

```python
client_name = serializers.CharField(source='client.name', read_only=True)
```

## 📈 Relatórios

### ViewSet de Relatórios

Endpoints em `apps/reports/views.py`:

- `/api/reports/sales_summary/` - Resumo de vendas
- `/api/reports/inventory_status/` - Status do estoque
- `/api/reports/top_products/` - Produtos mais vendidos
- `/api/reports/clients_summary/` - Resumo de clientes
- `/api/reports/appointments_summary/` - Resumo de agendamentos
- `/api/reports/dashboard/` - Dashboard geral

### Agregações

Utilizamos agregações do Django ORM:
- `Sum()`, `Count()`, `Avg()`
- `TruncDate()`, `TruncMonth()`
- Filtros por período

## 🔗 Integrações

### Estrutura Desacoplada

Integrações implementadas como serviços em `apps/integrations/services.py`:

1. **MercadoPagoService**: Pagamentos (mock)
2. **WhatsAppService**: Mensagens (mock)
3. **EmailService**: E-mails (mock)

### Padrão de Implementação

```python
class IntegrationService:
    @staticmethod
    def method():
        # Lógica da integração
        # Pode ser substituída por chamadas reais à API
        pass
```

## 🎨 Frontend (Vue.js 3)

### Estrutura

```
frontend/src/
├── views/           # Páginas
├── components/      # Componentes reutilizáveis
├── layouts/         # Layouts
├── router/          # Rotas
├── stores/          # Pinia stores
├── services/        # Serviços API
└── assets/          # CSS, imagens
```

### State Management (Pinia)

Store de autenticação em `stores/auth.js`:
- Token management
- User state
- Login/logout

### Services Layer

Camada de serviços para comunicação com API:
- `services/api.js` - Configuração do Axios
- `services/auth.js` - Autenticação
- `services/clients.js` - Clientes
- (outros serviços...)

### Router Guards

Proteção de rotas baseada em autenticação:

```javascript
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login' })
  }
})
```

## 🔒 Segurança

### Backend

- JWT Authentication
- Permissões por role
- Validação de dados nos models
- CORS configurado
- SQL injection protection (ORM)

### Frontend

- Token armazenado no localStorage
- Interceptors do Axios para adicionar token
- Redirecionamento em caso de 401

## 📚 Documentação da API

### Swagger/OpenAPI

Configurado com `drf-spectacular`:
- Endpoint: `/api/schema/swagger-ui/`
- Interface interativa
- Documentação automática

## 🚀 Escalabilidade

### Preparado para Multi-tenant

Estrutura permite adicionar multi-tenancy no futuro:
- Models podem incluir `tenant_id`
- Filtros automáticos por tenant
- Isolamento de dados

### Cache (Futuro)

Pontos onde cache pode ser implementado:
- Relatórios (Redis)
- Produtos mais vendidos
- Dashboard

### Async Tasks (Futuro)

Tarefas que podem ser assíncronas:
- Envio de e-mails
- Geração de PDFs
- Notificações WhatsApp

## 📦 Dependências Principais

### Backend

- Django 4.2+
- Django REST Framework
- djangorestframework-simplejwt
- drf-spectacular
- psycopg2-binary (PostgreSQL)
- python-decouple (configurações)

### Frontend

- Vue.js 3
- Vue Router 4
- Pinia
- Axios
- TailwindCSS
- Vite

## 🧪 Testes (Futuro)

Estrutura preparada para testes:
- Pytest para backend
- Vitest para frontend
- Testes de integração
- Testes de permissões
