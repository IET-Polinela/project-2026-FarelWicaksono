function isAuthenticated() {
  return Boolean(localStorage.getItem('access_token'));
}

function clearAuthData() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('username');
  localStorage.removeItem('citizen_username');
}

function logout() {
  clearAuthData();
  window.location.hash = '#login';
}

function setLoginLoading(isLoading) {
  const button = document.getElementById('loginSubmit');
  if (!button) return;

  button.disabled = isLoading;
  button.querySelector('.button-label')?.classList.toggle('d-none', isLoading);
  button.querySelector('.button-loading')?.classList.toggle('d-none', !isLoading);
}

function showLoginError(message) {
  const alertBox = document.getElementById('loginAlert');
  if (!alertBox) return;
  alertBox.textContent = message;
  alertBox.classList.remove('d-none');
}

function setupLoginForm() {
  const form = document.getElementById('loginForm');
  const passwordInput = document.getElementById('loginPassword');
  const togglePassword = document.getElementById('togglePassword');

  togglePassword?.addEventListener('click', () => {
    const showPassword = passwordInput.type === 'password';
    passwordInput.type = showPassword ? 'text' : 'password';
    togglePassword.innerHTML = `<i class="bi ${showPassword ? 'bi-eye-slash' : 'bi-eye'}"></i>`;
  });

  form?.addEventListener('submit', async (event) => {
    event.preventDefault();

    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;
    document.getElementById('loginAlert')?.classList.add('d-none');

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
      localStorage.setItem('username', username);

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
