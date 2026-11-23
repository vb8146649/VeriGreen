import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  timeout: 60000,
});

export async function startAudit(formData) {
  const res = await api.post('/audit', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

export async function getAudit(auditId) {
  const res = await api.get(`/audit/${auditId}`);
  return res.data;
}

export async function getAudits() {
  const res = await api.get('/audits');
  return res.data;
}

export async function getClaims(auditId, filters = {}) {
  const params = new URLSearchParams();
  if (filters.pillar) params.set('pillar', filters.pillar);
  if (filters.max_score) params.set('max_score', filters.max_score);
  if (filters.sort) params.set('sort', filters.sort);
  const res = await api.get(`/claims/${auditId}`, { params });
  return res.data;
}

export async function downloadReport(auditId) {
  const res = await api.get(`/report/${auditId}/download`, {
    responseType: 'blob',
  });
  return res.data;
}

export async function downloadBadge(claimId) {
  const res = await api.get(`/badge/${claimId}`, {
    responseType: 'blob',
  });
  return res.data;
}

export async function getHealth() {
  const res = await api.get('/health');
  return res.data;
}

export default api;
