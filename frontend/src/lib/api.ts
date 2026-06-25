import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

export const submitClaim = (data: {
  company_slug: string
  description: string
  customer_name?: string
  policy_number?: string
}) => api.post('/claims/submit', data).then(r => r.data)

export const getClaim = (id: string) => api.get(`/claims/${id}`).then(r => r.data)

export const listClaims = () => api.get('/claims/').then(r => r.data)

export const getMetrics = () => api.get('/admin/metrics').then(r => r.data)

export const getCompanies = () => api.get('/admin/companies').then(r => r.data)

export const getFlagged = () => api.get('/admin/flagged').then(r => r.data)

export const ingestPDF = (formData: FormData) =>
  api.post('/admin/ingest-pdf', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(r => r.data)

export default api
