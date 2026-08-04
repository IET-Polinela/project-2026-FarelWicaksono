# Changelog Lab Session 10

## File baru

- `main_app/serializers.py`
- `main_app/permissions.py`
- `main_app/api_views.py`
- `main_app/migrations/0003_report_reporter_and_draft_status.py`
- `usermanagement_24782049/serializers.py`
- `usermanagement_24782049/api_views.py`
- `requirements.txt`
- `Lab10_JWT.postman_collection.json`
- `LAB10_PANDUAN.md`
- `LAB10_JAWABAN_LOGBOOK.md`

## File yang diperbarui

- `24782049_iet_2026/settings.py`
- `24782049_iet_2026/urls.py`
- `main_app/models.py`
- `main_app/views.py`
- `main_app/admin.py`
- `main_app/tests.py`
- `usermanagement_24782049/tests.py`
- `README.md`

## Fitur utama

- JWT access dan refresh token.
- Registrasi akun Citizen.
- Report API dengan autentikasi.
- Reporter diambil dari `request.user`, bukan payload.
- Update/delete hanya untuk pemilik laporan DRAFT.
- Filter DRAFT berdasarkan pemilik.
- Automated API tests.
