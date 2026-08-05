function isAuthenticated() {
  return Boolean(localStorage.getItem('access_token'));
}

function clearAuthData() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('citizen_username');
}

function logout() {
  clearAuthData();
  window.location.hash = '#login';
}

function setLoginLoading(isLoading) {
  const button = document.getElementById('login-submit');
  if (!button) return;

  button.disabled = isLoading;
  button.querySelector('.button-label')?.classList.toggle('d-none', isLoading);
  button.querySelector('.button-loading')?.classList.toggle('d-none', !isLoading);
}

function showLoginError(message) {
  const alertBox = document.getElementById('login-alert');
  if (!alertBox) return;
  alertBox.textContent = message;
  alertBox.classList.remove('d-none');
}

function setupLoginForm() {
  const form = document.getElementById('login-form');
  const passwordInput = document.getElementById('login-password');
  const togglePassword = document.getElementById('toggle-password');

  togglePassword?.addEventListener('click', () => {
    const showPassword = passwordInput.type === 'password';
    passwordInput.type = showPassword ? 'text' : 'password';
    togglePassword.innerHTML = `<i class="bi ${showPassword ? 'bi-eye-slash' : 'bi-eye'}"></i>`;
  });

  form?.addEventListener('submit', async (event) => {
    event.preventDefault();

    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    document.getElementById('login-alert')?.classList.add('d-none');

    if (!username || !password) {
      showLoginError('Username dan password wajib diisi.');
      return;
    }

    setLoginLoading(true);
    try {
      const tokenData = await requestAPI(
        '/api/token/',
        'POST',
        { username, password },
        { auth: false },
      );

      localStorage.setItem('access_token', tokenData.access);
      localStorage.setItem('refresh_token', tokenData.refresh);
      localStorage.setItem('citizen_username', username);

      window.alert('Login berhasil. Selamat datang di Citizen Portal.');
      window.location.hash = '#dashboard';
    } catch (error) {
      showLoginError(error.status === 401
        ? 'Username atau password tidak sesuai.'
        : error.message);
    } finally {
      setLoginLoading(false);
    }
  });
}
