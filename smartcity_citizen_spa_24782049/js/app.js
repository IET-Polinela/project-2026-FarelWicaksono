function escapeHTML(value = '') {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function getStatusMeta(status) {
  const normalized = String(status || '').toUpperCase();
  const map = {
    DRAFT: { label: 'Draft', icon: 'bi-pencil-square', className: 'status-draft' },
    REPORTED: { label: 'Reported', icon: 'bi-megaphone', className: 'status-reported' },
    VERIFIED: { label: 'Verified', icon: 'bi-patch-check', className: 'status-verified' },
    IN_PROGRESS: { label: 'In Progress', icon: 'bi-arrow-repeat', className: 'status-in_progress' },
    RESOLVED: { label: 'Resolved', icon: 'bi-check-circle', className: 'status-resolved' },
  };
  return map[normalized] || { label: normalized || 'Unknown', icon: 'bi-circle', className: 'status-reported' };
}

function renderNavigation() {
  const nav = document.getElementById('nav-menu');
  if (!nav) return;

  if (isAuthenticated()) {
    nav.innerHTML = `
      <a class="btn btn-sm btn-outline-light" href="#dashboard">
        <i class="bi bi-grid me-1"></i> Dashboard
      </a>
      <button class="btn btn-sm btn-light" type="button" id="logout-button">
        <i class="bi bi-box-arrow-right me-1"></i> Keluar
      </button>
    `;
    document.getElementById('logout-button')?.addEventListener('click', logout);
  } else {
    nav.innerHTML = `
      <a class="btn btn-sm btn-light" href="#login">
        <i class="bi bi-box-arrow-in-right me-1"></i> Masuk
      </a>
    `;
  }
}

function renderLogin() {
  renderNavigation();
  document.getElementById('app-content').innerHTML = `
    <section class="auth-shell">
      <div class="card auth-card">
        <div class="row g-0">
          <div class="col-12 col-lg-5 auth-visual d-flex flex-column justify-content-between">
            <div>
              <div class="auth-icon mb-4"><i class="bi bi-buildings-fill"></i></div>
              <p class="text-uppercase fw-semibold small opacity-75 mb-2">Smart City</p>
              <h1 class="display-6 fw-bold">Satu portal untuk partisipasi warga.</h1>
              <p class="mt-3 mb-0 opacity-75">Masuk untuk memantau laporan kota melalui layanan API yang aman dengan JWT.</p>
            </div>
            <div class="mt-5 small opacity-75">
              <i class="bi bi-shield-lock me-1"></i> Autentikasi terlindungi oleh JSON Web Token
            </div>
          </div>
          <div class="col-12 col-lg-7 auth-form-panel d-flex align-items-center">
            <div class="w-100">
              <p class="section-title mb-2">Citizen Access</p>
              <h2 class="fw-bold mb-2">Selamat datang kembali</h2>
              <p class="text-secondary mb-4">Gunakan akun Citizen yang telah terdaftar pada backend Django.</p>

              <div id="login-alert" class="alert alert-danger d-none" role="alert"></div>

              <form id="login-form" novalidate>
                <div class="mb-3">
                  <label for="login-username" class="form-label fw-semibold">Username</label>
                  <div class="input-group">
                    <span class="input-group-text bg-white"><i class="bi bi-person"></i></span>
                    <input type="text" class="form-control" id="login-username" name="username" autocomplete="username" required>
                  </div>
                </div>
                <div class="mb-4">
                  <label for="login-password" class="form-label fw-semibold">Password</label>
                  <div class="input-group">
                    <span class="input-group-text bg-white"><i class="bi bi-key"></i></span>
                    <input type="password" class="form-control" id="login-password" name="password" autocomplete="current-password" required>
                    <button class="btn btn-outline-secondary" type="button" id="toggle-password" aria-label="Tampilkan password">
                      <i class="bi bi-eye"></i>
                    </button>
                  </div>
                </div>
                <button class="btn btn-primary w-100 py-2 fw-semibold" type="submit" id="login-submit">
                  <span class="button-label"><i class="bi bi-box-arrow-in-right me-1"></i> Masuk ke Portal</span>
                  <span class="button-loading d-none"><span class="spinner-border spinner-border-sm me-2"></span>Memproses...</span>
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </section>
  `;
}

function renderDashboardShell() {
  renderNavigation();
  const username = localStorage.getItem('citizen_username') || 'Citizen';

  document.getElementById('app-content').innerHTML = `
    <section class="portal-card hero-card p-4 p-lg-5 mb-4">
      <div class="d-flex flex-column flex-lg-row align-items-lg-center justify-content-between gap-3">
        <div>
          <p class="text-uppercase small fw-semibold opacity-75 mb-2">Citizen Dashboard</p>
          <h1 class="h2 fw-bold mb-2">Halo, ${escapeHTML(username)}</h1>
          <p class="mb-0 opacity-75">Pantau laporan dan perkembangan layanan kota dari satu tempat.</p>
        </div>
        <div class="d-flex gap-2">
          <button class="btn btn-light" type="button" id="refresh-dashboard">
            <i class="bi bi-arrow-clockwise me-1"></i> Muat Ulang
          </button>
        </div>
      </div>
    </section>

    <section class="row g-4">
      <aside class="col-12 col-lg-3">
        <div class="portal-card p-4 h-100">
          <p class="section-title">Profil Warga</p>
          <div class="d-flex align-items-center gap-3 mb-4">
            <div class="stat-icon"><i class="bi bi-person-badge"></i></div>
            <div>
              <div class="fw-bold">${escapeHTML(username)}</div>
              <div class="text-secondary small">Citizen terautentikasi</div>
            </div>
          </div>
          <div class="stat-chip mb-3">
            <div class="stat-icon"><i class="bi bi-shield-check"></i></div>
            <div><div class="fw-semibold">JWT Aktif</div><small class="text-secondary">Access token tersedia</small></div>
          </div>
          <div class="stat-chip">
            <div class="stat-icon"><i class="bi bi-hdd-network"></i></div>
            <div><div class="fw-semibold">API Terhubung</div><small class="text-secondary">127.0.0.1:8000</small></div>
          </div>
        </div>
      </aside>

      <div class="col-12 col-lg-6">
        <div class="portal-card p-4 h-100">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <div>
              <p class="section-title mb-1">Laporan Kota</p>
              <h2 class="h5 fw-bold mb-0">Aktivitas terbaru</h2>
            </div>
            <span class="badge text-bg-primary" id="report-count">0 laporan</span>
          </div>
          <div id="reports-container">
            <div class="empty-state">
              <div class="spinner-border spinner-border-sm text-primary mb-3" role="status"></div>
              <p class="mb-0">Mengambil data dari Django API...</p>
            </div>
          </div>
        </div>
      </div>

      <aside class="col-12 col-lg-3">
        <div class="portal-card p-4 mb-4">
          <p class="section-title">Ringkasan Status</p>
          <div id="status-summary" class="d-grid gap-3">
            <div class="text-secondary small">Data sedang dimuat...</div>
          </div>
        </div>
        <div class="portal-card p-4">
          <p class="section-title">Informasi</p>
          <div class="d-flex gap-3">
            <div class="stat-icon flex-shrink-0"><i class="bi bi-info-circle"></i></div>
            <p class="small text-secondary mb-0">Laporan DRAFT hanya terlihat oleh Citizen pemiliknya. Laporan non-DRAFT dapat dilihat seluruh pengguna yang sudah login.</p>
          </div>
        </div>
      </aside>
    </section>
  `;

  document.getElementById('refresh-dashboard')?.addEventListener('click', loadDashboardData);
}

function renderReports(reports) {
  const container = document.getElementById('reports-container');
  const count = document.getElementById('report-count');
  if (!container || !count) return;

  count.textContent = `${reports.length} laporan`;

  if (reports.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <i class="bi bi-inbox"></i>
        <h3 class="h6 fw-bold">Belum ada laporan</h3>
        <p class="mb-0">Data laporan akan tampil di bagian ini.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = reports.slice(0, 8).map((report) => {
    const status = getStatusMeta(report.status);
    const created = report.created_at
      ? new Intl.DateTimeFormat('id-ID', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(report.created_at))
      : '-';

    return `
      <article class="report-item">
        <div class="d-flex justify-content-between align-items-start gap-3">
          <div>
            <h3 class="h6 fw-bold mb-1">${escapeHTML(report.title)}</h3>
            <p class="small text-secondary mb-2">
              <i class="bi bi-geo-alt me-1"></i>${escapeHTML(report.location)}
              <span class="mx-1">&middot;</span>${escapeHTML(report.category)}
            </p>
            <small class="text-secondary"><i class="bi bi-clock me-1"></i>${escapeHTML(created)}</small>
          </div>
          <span class="status-badge ${status.className} flex-shrink-0">
            <i class="bi ${status.icon}"></i>${status.label}
          </span>
        </div>
      </article>
    `;
  }).join('');
}

function renderStatusSummary(reports) {
  const summary = document.getElementById('status-summary');
  if (!summary) return;

  const statuses = ['DRAFT', 'REPORTED', 'VERIFIED', 'IN_PROGRESS', 'RESOLVED'];
  const counts = Object.fromEntries(statuses.map((status) => [status, 0]));
  reports.forEach((report) => {
    if (Object.hasOwn(counts, report.status)) counts[report.status] += 1;
  });

  summary.innerHTML = statuses.map((status) => {
    const meta = getStatusMeta(status);
    return `
      <div class="d-flex justify-content-between align-items-center">
        <span class="status-badge ${meta.className}"><i class="bi ${meta.icon}"></i>${meta.label}</span>
        <strong>${counts[status]}</strong>
      </div>
    `;
  }).join('');
}

async function loadDashboardData() {
  const container = document.getElementById('reports-container');
  if (container) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="spinner-border spinner-border-sm text-primary mb-3" role="status"></div>
        <p class="mb-0">Mengambil data dari Django API...</p>
      </div>
    `;
  }

  try {
    const reports = await requestAPI('/api/reports/');
    renderReports(Array.isArray(reports) ? reports : []);
    renderStatusSummary(Array.isArray(reports) ? reports : []);
  } catch (error) {
    if (error.status === 401) {
      clearAuthData();
      window.location.hash = '#login';
      return;
    }

    if (container) {
      container.innerHTML = `
        <div class="alert alert-danger mb-0" role="alert">
          <i class="bi bi-exclamation-triangle me-2"></i>${escapeHTML(error.message)}
        </div>
      `;
    }
  }
}

async function renderDashboard() {
  renderDashboardShell();
  await loadDashboardData();
}

function renderNotFound() {
  renderNavigation();
  document.getElementById('app-content').innerHTML = `
    <section class="portal-card p-5 text-center mx-auto" style="max-width: 650px;">
      <div class="display-4 text-primary mb-3"><i class="bi bi-signpost-split"></i></div>
      <h1 class="h3 fw-bold">Halaman tidak ditemukan</h1>
      <p class="text-secondary">Rute yang diminta tidak tersedia pada Citizen Portal.</p>
      <a class="btn btn-primary" href="${isAuthenticated() ? '#dashboard' : '#login'}">Kembali</a>
    </section>
  `;
}
