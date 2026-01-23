# Sistema de Gestão para Pet Shop

Sistema web completo para gerenciamento de Pet Shop, desenvolvido com Django REST Framework no backend e Vue.js 3 no frontend.

## 🚀 Tecnologias

### Backend
- Django 4.2+
- Django REST Framework
- PostgreSQL
- JWT Authentication (djangorestframework-simplejwt)
- drf-spectacular (Swagger/OpenAPI)

### Frontend
- Vue.js 3
- Composition API
- Vue Router
- Pinia
- Axios
- TailwindCSS

## 📁 Estrutura do Projeto

```
petshop/
├── backend/          # API Django REST
│   ├── core/
│   ├── apps/
│   └── manage.py
├── frontend/         # Aplicação Vue.js
│   ├── src/
│   └── package.json
└── README.md
```

## 🛠️ Instalação

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 📋 Funcionalidades

- ✅ Gestão de Clientes e Animais
- ✅ Cadastro de Produtos e Controle de Estoque
- ✅ Serviços e Agendamentos
- ✅ Vendas e Faturamento
- ✅ Sistema de Usuários e Permissões (RBAC)
- ✅ Relatórios
- ✅ API REST Documentada
- ✅ Autenticação JWT

## 🔐 Perfis de Usuário

- **Administrador**: Acesso total ao sistema
- **Gerente**: Gerenciamento e relatórios
- **Usuário**: Operações básicas (vendas, cadastros)

## 📚 Documentação da API

Acesse `/api/schema/swagger-ui/` após iniciar o servidor Django para ver a documentação interativa da API.

## 🔗 Endpoints Principais

- `/api/auth/` - Autenticação JWT
- `/api/clients/` - Clientes
- `/api/pets/` - Animais
- `/api/products/` - Produtos
- `/api/services/` - Serviços
- `/api/scheduling/` - Agendamentos
- `/api/sales/` - Vendas

## 📝 Licença

Este projeto é privado e destinado ao uso interno.
