/* API configuration */
// In production: use relative URL so Vercel proxies /api/* to Railway (no CORS)
// In local dev: fall back to localhost:8000
const isDev = import.meta.env.DEV;
export const API_BASE_URL = isDev
  ? (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000')
  : '';  // empty = same origin → Vercel proxy handles it
export const WS_BASE_URL = isDev
  ? (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace('http', 'ws')
  : `wss://signspeak-backend-production.up.railway.app`;  // WS still goes direct

/* API helper with auth */
export async function apiFetch(path, options = {}) {
  const token = localStorage.getItem('signspeak_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    localStorage.removeItem('signspeak_token');
    localStorage.removeItem('signspeak_user');
    window.location.href = '/login';
    return;
  }

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'An error occurred');
  }

  return data;
}
