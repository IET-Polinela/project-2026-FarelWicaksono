const API_BASE_URL = 'http://127.0.0.1:8000';

class APIError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
}

async function requestAPI(endpoint, method = 'GET', bodyData = null, options = {}) {
  const { auth = true } = options;
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

  const contentType = response.headers.get('content-type') || '';
  const data = contentType.includes('application/json')
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const message = data?.detail
      || data?.non_field_errors?.[0]
      || 'Permintaan ke API gagal.';
    throw new APIError(message, response.status, data);
  }

  return data;
}
