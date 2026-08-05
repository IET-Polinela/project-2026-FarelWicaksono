let currentTab = 'my_reports';
let currentPage = 1;
let editingReportId = null;
const REPORT_PAGE_SIZE = 10;

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
    DRAFT: { label: 'Draft', icon: 'bi-pencil-square', className: 'status-draft', progress: 10 },
    REPORTED: { label: 'Reported', icon: 'bi-megaphone', className: 'status-reported', progress: 35 },
    VERIFIED: { label: 'Verified', icon: 'bi-patch-check', className: 'status-verified', progress: 60 },
    IN_PROGRESS: { label: 'In Progress', icon: 'bi-arrow-repeat', className: 'status-in_progress', progress: 80 },
    RESOLVED: { label: 'Resolved', icon: 'bi-check-circle', className: 'status-resolved', progress: 100 },
  };
  return map[normalized] || {
    label: normalized || 'Unknown',
    icon: 'bi-circle',
    className: 'status-reported',
    progress: 0,
  };
}

function formatDate(value) {
  if (!value) return '-';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '-';
  return new Intl.DateTimeFormat('id-ID', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date);
}

function normalizePaginatedData(data) {
  if (Array.isArray(data)) {
    return { count: data.length, next: null, previous: null, results: data };
  }
  return {
    count: Number(data?.count || 0),
    next: data?.next || null,
    previous: data?.previous || null,
    results: Array.isArray(data?.results) ? data.results : [],
  };
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
              <p class="mt-3 mb-0 opacity-75">Masuk untuk mengelola laporan kota melalui API yang aman dan teroptimasi.</p>
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
          <p class="mb-0 opacity-75">Kelola laporan pribadi dan pantau Feed Kota tanpa memuat ulang halaman.</p>
        </div>
        <div class="d-flex flex-wrap gap-2">
          <button class="btn btn-outline-light" type="button" id="refresh-dashboard">
            <i class="bi bi-arrow-clockwise me-1"></i> Muat Ulang
          </button>
          <button class="btn btn-light" type="button" id="new-report-button">
            <i class="bi bi-plus-circle me-1"></i> Tambah Laporan Baru
          </button>
        </div>
      </div>
    </section>

    <section class="row g-4">
      <aside class="col-12 col-lg-3">
        <div class="portal-card p-4 mb-4">
          <p class="section-title">Profil Warga</p>
          <div class="d-flex align-items-center gap-3">
            <div class="stat-icon"><i class="bi bi-person-badge"></i></div>
            <div>
              <div class="fw-bold">${escapeHTML(username)}</div>
              <div class="text-secondary small">Citizen terautentikasi</div>
            </div>
          </div>
        </div>

        <div class="portal-card p-4">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <p class="section-title mb-0">Rekap Status Saya</p>
            <i class="bi bi-bar-chart text-primary"></i>
          </div>
          <div id="status-summary" class="d-grid gap-3">
            <div class="text-secondary small">Menghitung laporan...</div>
          </div>
        </div>
      </aside>

      <div class="col-12 col-lg-6">
        <div class="portal-card p-3 p-md-4 h-100">
          <div class="d-flex flex-column gap-3 mb-4">
            <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
              <div>
                <p class="section-title mb-1">Laporan Kota</p>
                <h2 class="h5 fw-bold mb-0" id="list-heading">Laporan Saya</h2>
              </div>
              <span class="badge text-bg-primary align-self-start align-self-md-center" id="report-count">0 laporan</span>
            </div>
            <div class="nav nav-pills report-tabs" role="tablist" aria-label="Pilih daftar laporan">
              <button class="nav-link active" type="button" data-report-tab="my_reports">
                <i class="bi bi-person-lines-fill me-1"></i>Laporan Saya
              </button>
              <button class="nav-link" type="button" data-report-tab="feed">
                <i class="bi bi-globe2 me-1"></i>Feed Kota
              </button>
            </div>
            <small class="text-secondary">
              <i class="bi bi-sort-down me-1"></i>Diurutkan berdasarkan pembaruan terbaru.
            </small>
          </div>

          <div id="reports-container">
            <div class="empty-state">
              <div class="spinner-border spinner-border-sm text-primary mb-3" role="status"></div>
              <p class="mb-0">Mengambil data dari Django API...</p>
            </div>
          </div>
          <nav class="mt-4" aria-label="Navigasi halaman laporan">
            <div id="pagination-container"></div>
          </nav>
        </div>
      </div>

      <aside class="col-12 col-lg-3">
        <div class="portal-card p-4 mb-4">
          <p class="section-title">Status Sistem</p>
          <div class="stat-chip mb-3">
            <div class="stat-icon"><i class="bi bi-shield-check"></i></div>
            <div><div class="fw-semibold">JWT Aktif</div><small class="text-secondary">Bearer Token otomatis</small></div>
          </div>
          <div class="stat-chip">
            <div class="stat-icon"><i class="bi bi-hdd-network"></i></div>
            <div><div class="fw-semibold">API Terhubung</div><small class="text-secondary">127.0.0.1:8000</small></div>
          </div>
        </div>
        <div class="portal-card p-4">
          <p class="section-title">Aturan Akses</p>
          <div class="d-flex gap-3 mb-3">
            <div class="stat-icon flex-shrink-0"><i class="bi bi-pencil"></i></div>
            <p class="small text-secondary mb-0">Tombol Edit hanya tersedia untuk laporan milik sendiri yang masih DRAFT.</p>
          </div>
          <div class="d-flex gap-3">
            <div class="stat-icon flex-shrink-0"><i class="bi bi-incognito"></i></div>
            <p class="small text-secondary mb-0">Identitas pelapor pada Feed Kota disensor oleh API menjadi Warga Anonim.</p>
          </div>
        </div>
      </aside>
    </section>
  `;

  document.getElementById('refresh-dashboard')?.addEventListener('click', () => {
    loadDashboardData(currentTab, currentPage);
  });
  document.getElementById('new-report-button')?.addEventListener('click', openCreateReportModal);
  document.querySelectorAll('[data-report-tab]').forEach((button) => {
    button.addEventListener('click', () => switchReportTab(button.dataset.reportTab));
  });
  setupReportModal();
}

function renderReportList(reports, tab) {
  const container = document.getElementById('reports-container');
  if (!container) return;

  if (reports.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <i class="bi ${tab === 'feed' ? 'bi-globe2' : 'bi-inbox'}"></i>
        <h3 class="h6 fw-bold">Belum ada laporan</h3>
        <p class="mb-0">${tab === 'feed'
          ? 'Belum ada laporan publik dari warga lain.'
          : 'Gunakan tombol Tambah Laporan Baru untuk membuat laporan.'}</p>
      </div>
    `;
    return;
  }

  container.innerHTML = reports.map((report) => {
    const status = getStatusMeta(report.status);
    const canEdit = tab === 'my_reports' && report.is_owner && report.status === 'DRAFT';
    const reporterLabel = tab === 'feed' ? 'Warga Anonim' : report.reporter;

    return `
      <article class="report-card mb-3">
        <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-start gap-3">
          <div class="flex-grow-1">
            <div class="d-flex flex-wrap gap-2 align-items-center mb-2">
              <span class="status-badge ${status.className}"><i class="bi ${status.icon}"></i>${status.label}</span>
              <span class="small text-secondary"><i class="bi bi-person-circle me-1"></i>${escapeHTML(reporterLabel)}</span>
            </div>
            <h3 class="h5 fw-bold mb-2">${escapeHTML(report.title)}</h3>
            <p class="text-secondary report-description mb-3">${escapeHTML(report.description)}</p>
            <div class="d-flex flex-wrap gap-x-3 gap-y-2 small text-secondary">
              <span><i class="bi bi-geo-alt me-1"></i>${escapeHTML(report.location)}</span>
              <span><i class="bi bi-tag me-1"></i>${escapeHTML(report.category)}</span>
              <span><i class="bi bi-clock-history me-1"></i>${escapeHTML(formatDate(report.updated_at || report.created_at))}</span>
            </div>
          </div>
          ${canEdit ? `
            <button class="btn btn-sm btn-outline-primary flex-shrink-0" type="button" data-edit-report="${report.id}">
              <i class="bi bi-pencil-square me-1"></i>Edit
            </button>
          ` : ''}
        </div>
        <div class="mt-4">
          <div class="d-flex justify-content-between small mb-1">
            <span class="fw-semibold">Progress Penanganan</span>
            <span>${status.progress}%</span>
          </div>
          <div class="progress" role="progressbar" aria-label="Progress ${escapeHTML(status.label)}" aria-valuenow="${status.progress}" aria-valuemin="0" aria-valuemax="100">
            <div class="progress-bar progress-${String(report.status).toLowerCase()}" style="width: ${status.progress}%"></div>
          </div>
        </div>
      </article>
    `;
  }).join('');

  container.querySelectorAll('[data-edit-report]').forEach((button) => {
    button.addEventListener('click', () => editDraft(button.dataset.editReport));
  });
}

function renderPagination(paginated, page) {
  const container = document.getElementById('pagination-container');
  if (!container) return;

  const totalPages = Math.max(1, Math.ceil(paginated.count / REPORT_PAGE_SIZE));
  if (paginated.count <= REPORT_PAGE_SIZE) {
    container.innerHTML = '';
    return;
  }

  const start = Math.max(1, page - 2);
  const end = Math.min(totalPages, page + 2);
  const pageButtons = [];
  for (let number = start; number <= end; number += 1) {
    pageButtons.push(`
      <li class="page-item ${number === page ? 'active' : ''}">
        <button class="page-link" type="button" data-page="${number}">${number}</button>
      </li>
    `);
  }

  container.innerHTML = `
    <div class="d-flex flex-column flex-sm-row justify-content-between align-items-sm-center gap-2">
      <small class="text-secondary">Halaman ${page} dari ${totalPages} &middot; ${paginated.count} data</small>
      <ul class="pagination pagination-sm mb-0">
        <li class="page-item ${paginated.previous ? '' : 'disabled'}">
          <button class="page-link" type="button" data-page="${page - 1}" ${paginated.previous ? '' : 'disabled'} aria-label="Sebelumnya">
            <i class="bi bi-chevron-left"></i>
          </button>
        </li>
        ${pageButtons.join('')}
        <li class="page-item ${paginated.next ? '' : 'disabled'}">
          <button class="page-link" type="button" data-page="${page + 1}" ${paginated.next ? '' : 'disabled'} aria-label="Berikutnya">
            <i class="bi bi-chevron-right"></i>
          </button>
        </li>
      </ul>
    </div>
  `;

  container.querySelectorAll('[data-page]').forEach((button) => {
    button.addEventListener('click', () => {
      const targetPage = Number(button.dataset.page);
      if (targetPage >= 1 && targetPage <= totalPages && targetPage !== currentPage) {
        loadDashboardData(currentTab, targetPage);
      }
    });
  });
}

function renderStatusSummary(reports) {
  const summary = document.getElementById('status-summary');
  if (!summary) return;

  const statuses = ['DRAFT', 'REPORTED', 'VERIFIED', 'IN_PROGRESS', 'RESOLVED'];
  const counts = Object.fromEntries(
    statuses.map((status) => [
      status,
      reports.filter((report) => report.status === status).length,
    ]),
  );

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

async function loadSummaryStats() {
  try {
    const data = await requestAPI('/api/reports/?tab=my_reports&page_size=1000&page=1');
    renderStatusSummary(normalizePaginatedData(data).results);
  } catch (error) {
    const summary = document.getElementById('status-summary');
    if (summary) summary.innerHTML = '<div class="text-danger small">Rekap gagal dimuat.</div>';
  }
}

async function loadDashboardData(tab = currentTab, page = currentPage) {
  currentTab = tab;
  currentPage = page;

  const container = document.getElementById('reports-container');
  const paginationContainer = document.getElementById('pagination-container');
  if (container) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="spinner-border spinner-border-sm text-primary mb-3" role="status"></div>
        <p class="mb-0">Mengambil halaman ${page} dari Django API...</p>
      </div>
    `;
  }
  if (paginationContainer) paginationContainer.innerHTML = '';

  try {
    const data = await requestAPI(`/api/reports/?tab=${encodeURIComponent(tab)}&page=${page}`);
    const paginated = normalizePaginatedData(data);

    document.getElementById('report-count').textContent = `${paginated.count} laporan`;
    document.getElementById('list-heading').textContent = tab === 'feed' ? 'Feed Kota' : 'Laporan Saya';
    renderReportList(paginated.results, tab);
    renderPagination(paginated, page);
    await loadSummaryStats();
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

function switchReportTab(tab) {
  if (!['my_reports', 'feed'].includes(tab) || tab === currentTab) return;
  document.querySelectorAll('[data-report-tab]').forEach((button) => {
    button.classList.toggle('active', button.dataset.reportTab === tab);
  });
  loadDashboardData(tab, 1);
}

function getReportModal() {
  const element = document.getElementById('reportModal');
  return element ? bootstrap.Modal.getOrCreateInstance(element) : null;
}

function setReportFormAlert(message = '') {
  const alertBox = document.getElementById('report-form-alert');
  if (!alertBox) return;
  alertBox.textContent = message;
  alertBox.classList.toggle('d-none', !message);
}

function resetReportForm() {
  editingReportId = null;
  const form = document.getElementById('report-form');
  form?.reset();
  form?.classList.remove('was-validated');
  setReportFormAlert();
  const title = document.getElementById('reportModalLabel');
  if (title) title.textContent = 'Buat Laporan Baru';
}

function openCreateReportModal() {
  resetReportForm();
  getReportModal()?.show();
}

async function editDraft(id) {
  try {
    const report = await requestAPI(`/api/reports/${id}/`);
    if (!report.is_owner || report.status !== 'DRAFT') {
      throw new APIError('Hanya draft milik sendiri yang dapat diedit.', 403);
    }

    editingReportId = Number(id);
    document.getElementById('report-title').value = report.title || '';
    document.getElementById('report-category').value = report.category || '';
    document.getElementById('report-location').value = report.location || '';
    document.getElementById('report-description').value = report.description || '';
    document.getElementById('reportModalLabel').textContent = `Edit Draft #${report.id}`;
    setReportFormAlert();
    getReportModal()?.show();
  } catch (error) {
    window.alert(error.message);
  }
}

function setReportActionLoading(activeButton, isLoading) {
  ['save-draft-button', 'submit-report-button'].forEach((id) => {
    const button = document.getElementById(id);
    if (!button) return;
    button.disabled = isLoading;
    const isActive = button === activeButton;
    button.querySelector('.action-label')?.classList.toggle('d-none', isLoading && isActive);
    button.querySelector('.action-loading')?.classList.toggle('d-none', !(isLoading && isActive));
  });
}

async function submitReport(targetStatus, activeButton) {
  const form = document.getElementById('report-form');
  if (!form) return;

  form.classList.add('was-validated');
  if (!form.checkValidity()) return;

  const payload = {
    title: document.getElementById('report-title').value.trim(),
    category: document.getElementById('report-category').value,
    location: document.getElementById('report-location').value.trim(),
    description: document.getElementById('report-description').value.trim(),
    status: targetStatus,
  };
  const method = editingReportId === null ? 'POST' : 'PUT';
  const endpoint = editingReportId === null
    ? '/api/reports/'
    : `/api/reports/${editingReportId}/`;

  setReportFormAlert();
  setReportActionLoading(activeButton, true);
  try {
    await requestAPI(endpoint, method, payload);
    getReportModal()?.hide();
    resetReportForm();
    currentTab = 'my_reports';
    currentPage = 1;
    document.querySelectorAll('[data-report-tab]').forEach((button) => {
      button.classList.toggle('active', button.dataset.reportTab === 'my_reports');
    });
    await loadDashboardData('my_reports', 1);
  } catch (error) {
    setReportFormAlert(error.message);
  } finally {
    setReportActionLoading(activeButton, false);
  }
}

function setupReportModal() {
  const saveButton = document.getElementById('save-draft-button');
  const submitButton = document.getElementById('submit-report-button');
  const modalElement = document.getElementById('reportModal');
  if (!saveButton || !submitButton || !modalElement || modalElement.dataset.bound === 'true') return;

  modalElement.dataset.bound = 'true';
  saveButton.addEventListener('click', () => submitReport('DRAFT', saveButton));
  submitButton.addEventListener('click', () => submitReport('REPORTED', submitButton));
  document.getElementById('report-form')?.addEventListener('submit', (event) => event.preventDefault());
  modalElement.addEventListener('hidden.bs.modal', resetReportForm);
}

async function renderDashboard() {
  currentTab = 'my_reports';
  currentPage = 1;
  renderDashboardShell();
  await loadDashboardData(currentTab, currentPage);
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
