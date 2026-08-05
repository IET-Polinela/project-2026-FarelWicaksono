const API_BASE_URL = 'http://127.0.0.1:8000';

class APIError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
}

async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) return false;

  const response = await fetch(`${API_BASE_URL}/api/token/refresh/`, {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh: refreshToken }),
  });

  if (!response.ok) return false;
  const data = await response.json();
  localStorage.setItem('access_token', data.access);
  return true;
}

async function requestAPI(endpoint, method = 'GET', bodyData = null, options = {}) {
  const { auth = true, retry = true } = options;
  const headers = { Accept: 'application/json' };
  const accessToken = localStorage.getItem('access_token');

  if (bodyData !== null) {
    headers['Content-Type'] = 'application/json';
  }

  if (auth && accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method,
      headers,
      body: bodyData !== null ? JSON.stringify(bodyData) : null,
    });
  } catch (error) {
    throw new APIError(
      'Backend Django tidak dapat dihubungi. Pastikan server berjalan pada port 8000.',
      0,
      error,
    );
  }

  if (response.status === 401 && auth && retry) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      return requestAPI(endpoint, method, bodyData, { ...options, retry: false });
    }
  }

  const contentType = response.headers.get('content-type') || '';
  let data = null;
  if (response.status !== 204) {
    data = contentType.includes('application/json')
      ? await response.json()
      : await response.text();
  }

  if (!response.ok) {
    const firstFieldError = data && typeof data === 'object'
      ? Object.values(data).flat().find((item) => typeof item === 'string')
      : null;
    const message = data?.detail
      || data?.non_field_errors?.[0]
      || firstFieldError
      || 'Permintaan ke API gagal.';
    throw new APIError(message, response.status, data);
  }

  return data;
}
