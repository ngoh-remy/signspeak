/* API configuration */
export const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').trim();
export const WS_BASE_URL = API_BASE_URL.replace('http', 'ws');
export const HF_WS_BASE_URL = (import.meta.env.VITE_HF_WS_URL || WS_BASE_URL).trim();



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
