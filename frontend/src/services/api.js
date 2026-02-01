import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchTickets = async () => {
  const response = await api.get('/tickets');
  return response.data.data; // Assuming API returns { success: true, data: [...] }
};

export const fetchAuditLog = async () => {
  const response = await api.get('/audit-log');
  return response.data.data;
};

export const runAnalysis = async () => {
  const response = await api.post('/process-all');
  return response.data;
};

export const approveAction = async (ticketId) => {
  const response = await api.post('/approve', { ticket_id: ticketId });
  return response.data;
};

export const clearAuditLog = async () => {
  const response = await api.post('/clear-audit-log');
  return response.data;
};

export const rejectAction = async (ticketId, reason = 'Rejected by operator') => {
  const response = await api.post('/reject', { ticket_id: ticketId, reason });
  return response.data;
};

export const generateTickets = async (count = 5) => {
  const response = await api.post('/generate-tickets', { count });
  return response.data;
};

export default api;
