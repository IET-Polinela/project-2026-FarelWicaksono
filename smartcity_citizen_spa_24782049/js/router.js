const routes = {
  login: async () => {
    if (isAuthenticated()) {
      window.location.hash = '#dashboard';
      return;
    }
    renderLogin();
    setupLoginForm();
  },
  dashboard: async () => {
    if (!isAuthenticated()) {
      window.location.hash = '#login';
      return;
    }
    await renderDashboard();
  },
};

async function handleRouting() {
  const routeName = window.location.hash.replace(/^#/, '') || (isAuthenticated() ? 'dashboard' : 'login');
  const routeHandler = routes[routeName];

  if (!routeHandler) {
    renderNotFound();
    return;
  }

  await routeHandler();
}

window.addEventListener('hashchange', handleRouting);
window.addEventListener('DOMContentLoaded', handleRouting);
