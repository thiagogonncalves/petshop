# Módulo de Agendamentos – Guia de Uso

## Visão Geral

O módulo de Agendamentos permite gerenciar agendamentos de serviços (banho, tosa, etc.) e oferece **autoagendamento pelo celular** para clientes.

## Funcionalidades

- **Área interna (admin)**: Gerenciar agenda, configurações de horário
- **Portal público (mobile)**: Cliente agenda sozinho pelo celular
- **Cliente novo**: Cadastro rápido no fluxo de agendamento (CPF + nome + telefone + pet)
- **Cliente existente**: Verifica CPF, seleciona pet, agenda

## Configurações (Admin → Configurações)

1. **Horário de funcionamento**
   - Intervalo do slot (ex: 30 min)
   - Dias da semana abertos (Seg–Dom)
   - Horário de abertura/fechamento por dia
   - Pausa (ex: almoço 12:00–13:00)

2. **Datas de fechamento**
   - Feriados, folgas (ex: 25/12, 01/01)

## URLs Públicas (sem login)

- **Agendar**: `/agendar` – wizard de autoagendamento
- **Meus agendamentos**: `/agendar/meus` – lista por CPF

## API Pública (sem autenticação)

- `POST /api/public/booking/check-cpf/` – Verifica se CPF existe
- `POST /api/public/booking/register/` – Cadastra cliente + pet (novo)
- `GET /api/public/booking/available-slots/?service_id=1&date=2026-02-15` – Horários disponíveis
- `POST /api/public/booking/appointments/` – Cria agendamento
- `GET /api/public/booking/services/` – Lista serviços ativos
- `GET /api/public/booking/my-appointments/?cpf=12345678901` – Agendamentos do cliente

## Fluxo do Cliente (Autoagendamento)

1. Acessa `/agendar`
2. Informa CPF
3. **Se CPF existe**: confirma nome, seleciona pet
4. **Se CPF não existe**: cadastra nome, telefone, nome do pet, espécie
5. Seleciona serviço
6. Escolhe data
7. Escolhe horário disponível (slots)
8. Confirma agendamento

## Migrations

```bash
cd backend
python manage.py migrate scheduling
```

## Como testar

1. **Configurar horários**: Admin → Configurações → definir dias/horários
2. **Criar serviços**: Cadastro → Serviços (com duration_minutes)
3. **Testar portal**: Acesse `/agendar` (sem login)
4. **Cliente novo**: CPF inexistente → cadastro → pet → serviço → data → horário
5. **Cliente existente**: CPF cadastrado → pet → serviço → data → horário
