# Panduan Menjalankan Lab Session 10 — JWT Authentication

Project Lab 9 telah dilanjutkan dengan Django REST Framework, SimpleJWT, registrasi Citizen, ReportViewSet, filter laporan DRAFT, dan object-level permission.

## 1. Instalasi

Buka PowerShell pada folder yang berisi `manage.py`, kemudian jalankan:

```powershell
py -m pip install -r requirements.txt
```

Project secara default menggunakan PostgreSQL dengan database `smartcity_db`. Kredensial dapat diatur melalui environment variable `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, dan `DB_PORT`.

## 2. Migrasi database

```powershell
py manage.py migrate
```

Migration `0003_report_reporter_and_draft_status.py` akan:

1. Menambahkan field `reporter` pada model Report.
2. Menambahkan status `DRAFT` dan menjadikannya status default.
3. Menyeragamkan data lama `IN PROGRESS` menjadi `IN_PROGRESS`.

Field `reporter` dibuat nullable agar data Lab 9 yang sudah ada tidak gagal saat migrasi. Semua laporan baru dari API selalu memiliki reporter karena diisi oleh server melalui `perform_create()`.

## 3. Menjalankan server

```powershell
py manage.py runserver
```

Base URL Postman:

```text
http://127.0.0.1:8000
```

## 4. Endpoint Lab 10

| Method | Endpoint | Fungsi |
|---|---|---|
| POST | `/api/register/` | Registrasi Citizen baru |
| POST | `/api/token/` | Login dan memperoleh access/refresh token |
| POST | `/api/token/refresh/` | Memperbarui access token |
| GET | `/api/reports/` | Mengambil daftar laporan |
| POST | `/api/reports/` | Membuat laporan Citizen |
| GET | `/api/reports/{id}/` | Mengambil detail laporan |
| PUT/PATCH | `/api/reports/{id}/` | Mengubah laporan milik sendiri yang masih DRAFT |
| DELETE | `/api/reports/{id}/` | Menghapus laporan milik sendiri yang masih DRAFT |

## 5. Urutan pengujian Postman

### A. Registrasi Citizen

`POST /api/register/`

```json
{
  "username": "citizen_lab10",
  "email": "citizen10@example.com",
  "password": "PasswordKuat123!",
  "password2": "PasswordKuat123!"
}
```

Hasil yang diharapkan: `201 Created`.

### B. Login JWT

`POST /api/token/`

```json
{
  "username": "citizen_lab10",
  "password": "PasswordKuat123!"
}
```

Salin nilai `access`. Pada request berikutnya gunakan tab **Authorization → Bearer Token**:

```text
Bearer <access_token>
```

### C. Membuat laporan tanpa field reporter

`POST /api/reports/`

```json
{
  "title": "Banjir di Jalan Utama",
  "category": "Drainase",
  "description": "Air meluap dan menggenangi jalan warga.",
  "location": "Jalan Utama, Bimasakti City"
}
```

Jangan kirim `reporter` dan `status`. Server otomatis mengisi:

- `reporter` dari user yang terdapat pada access token.
- `status` menjadi `DRAFT`.

### D. GET ALL Report

`GET /api/reports/`

Citizen akan melihat:

- Semua laporan non-DRAFT.
- Laporan DRAFT miliknya sendiri.
- DRAFT milik Citizen lain tidak ditampilkan.

### E. PUT Report DRAFT milik sendiri

`PUT /api/reports/{id}/`

```json
{
  "title": "Banjir di Jalan Utama — Diperbarui",
  "category": "Drainase",
  "description": "Ketinggian air bertambah setelah hujan deras.",
  "location": "Jalan Utama, Bimasakti City"
}
```

Hasil yang diharapkan: `200 OK`.

### F. DELETE Report VERIFIED — harus gagal

Agar status laporan menjadi `VERIFIED`, buat superuser lalu ubah status melalui Django Admin:

```powershell
py manage.py createsuperuser
```

Buka `http://127.0.0.1:8000/admin/`, pilih Report, lalu ubah status laporan dari `DRAFT` menjadi `VERIFIED`.

Setelah itu, login kembali sebagai Citizen dan kirim:

```text
DELETE /api/reports/{id}/
```

Hasil yang diharapkan: `403 Forbidden` karena laporan tidak lagi berstatus DRAFT.

### G. Refresh Access Token

`POST /api/token/refresh/`

```json
{
  "refresh": "<refresh_token>"
}
```

Hasilnya adalah access token baru tanpa login ulang.

## 6. Menjalankan automated test

Untuk test cepat dengan SQLite tanpa mengubah konfigurasi PostgreSQL utama:

```powershell
$env:USE_SQLITE="1"
py manage.py test
Remove-Item Env:USE_SQLITE
```

Test mencakup registrasi, login JWT, create tanpa reporter, filter DRAFT, update DRAFT, penolakan admin pada create Citizen, penolakan DELETE VERIFIED, dan akses tanpa token.

## 7. File utama untuk screenshot kode

- `main_app/permissions.py`
- `main_app/api_views.py`
- `main_app/serializers.py`
- `usermanagement_24782049/serializers.py`
- `usermanagement_24782049/api_views.py`
- `24782049_iet_2026/settings.py`
- `24782049_iet_2026/urls.py`
