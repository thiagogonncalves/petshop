# Frontend - Pet Shop Management System

## 🚀 Início Rápido

### Pré-requisitos

- Node.js 16+
- npm ou yarn

### Instalação

1. **Instalar dependências:**

```bash
npm install
```

2. **Iniciar servidor de desenvolvimento:**

```bash
npm run dev
```

O aplicativo estará disponível em `http://localhost:5173`

3. **Build para produção:**

```bash
npm run build
```

Os arquivos serão gerados na pasta `dist/`

## 🏗️ Estrutura do Projeto

```
frontend/
├── src/
│   ├── views/          # Páginas
│   ├── components/     # Componentes reutilizáveis
│   ├── layouts/        # Layouts
│   ├── router/         # Configuração de rotas
│   ├── stores/         # Stores Pinia
│   ├── services/       # Serviços API
│   └── assets/         # CSS, imagens
├── index.html
└── package.json
```

## 🔧 Configuração

### API Backend

O proxy para o backend está configurado no `vite.config.js`:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

Certifique-se de que o backend está rodando em `http://localhost:8000`

## 🎨 Tecnologias

- **Vue.js 3**: Framework JavaScript
- **Vue Router**: Roteamento
- **Pinia**: Gerenciamento de estado
- **Axios**: Cliente HTTP
- **TailwindCSS**: Framework CSS utilitário
- **Vite**: Build tool

## 📱 Funcionalidades

- ✅ Autenticação JWT
- ✅ Dashboard com indicadores
- ✅ Gestão de Clientes
- ✅ Gestão de Animais
- ✅ Gestão de Produtos
- ✅ Gestão de Serviços
- ✅ Agendamentos
- ✅ Vendas
- ✅ Relatórios (Admin/Manager)

## 🔐 Autenticação

O token JWT é armazenado no `localStorage` e automaticamente incluído nas requisições via interceptor do Axios.

**Login:**
```javascript
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
await authStore.login(username, password)
```

**Logout:**
```javascript
authStore.logout()
```

**Verificar autenticação:**
```javascript
const isAuthenticated = authStore.isAuthenticated
const userRole = authStore.userRole
const isAdmin = authStore.isAdmin
```

## 🛣️ Rotas

- `/login` - Página de login
- `/` - Dashboard
- `/clients` - Clientes
- `/pets` - Animais
- `/products` - Produtos
- `/services` - Serviços
- `/scheduling` - Agendamentos
- `/sales` - Vendas
- `/reports` - Relatórios (apenas Admin/Manager)

Todas as rotas (exceto `/login`) requerem autenticação.

## 🎯 Desenvolvimento

### Adicionar Nova View

1. Crie o arquivo em `src/views/`
2. Adicione a rota em `src/router/index.js`
3. Adicione link no menu em `src/layouts/DefaultLayout.vue`

### Adicionar Novo Serviço API

Crie um arquivo em `src/services/`:

```javascript
import api from './api'

export const myService = {
  getAll() {
    return api.get('/my-endpoint/')
  },
  // ...
}
```

### Adicionar Nova Store Pinia

Crie um arquivo em `src/stores/`:

```javascript
import { defineStore } from 'pinia'

export const useMyStore = defineStore('myStore', {
  state: () => ({
    // state
  }),
  getters: {
    // getters
  },
  actions: {
    // actions
  },
})
```
