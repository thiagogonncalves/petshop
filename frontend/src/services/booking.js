/** API pública de autoagendamento (sem auth) */
import axios from 'axios'

const bookingApi = axios.create({
  baseURL: '/api/public/booking',
  headers: { 'Content-Type': 'application/json' },
})

export const bookingService = {
  checkCpf(cpf) {
    return bookingApi.post('/check-cpf/', { cpf: String(cpf).replace(/\D/g, '') })
  },
  register(data) {
    return bookingApi.post('/register/', data)
  },
  getAvailableSlots(serviceId, dateStr, excludeAppointmentId = null) {
    const params = { service_id: serviceId, date: dateStr }
    if (excludeAppointmentId) params.exclude_appointment_id = excludeAppointmentId
    return bookingApi.get('/available-slots/', { params })
  },
  createAppointment(data) {
    return bookingApi.post('/appointments/', data)
  },
  getServices() {
    return bookingApi.get('/services/')
  },
  getMyAppointments(cpf) {
    return bookingApi.get('/my-appointments/', { params: { cpf: String(cpf).replace(/\D/g, '') } })
  },
}
