# Jawaban Pertanyaan Lab Session 10

> Pertanyaan tetap perlu ditulis kembali dan jawaban ditulis tangan pada LogBook sesuai instruksi modul.

## 1. Cara Django memvalidasi Access Token JWT

Klien mengirim access token melalui header `Authorization: Bearer <token>`. `JWTAuthentication` membaca token tersebut, memecah tiga bagian JWT, lalu memverifikasi tanda tangan digitalnya menggunakan kunci dan algoritma yang dikonfigurasi server. Karena tanda tangan hanya dapat dibuat dengan kunci server yang sah, perubahan terhadap isi token menyebabkan verifikasi gagal. Server juga memeriksa claim waktu, terutama `exp`, untuk memastikan token belum kedaluwarsa. Setelah token dinyatakan valid, claim identitas pengguna, umumnya `user_id`, digunakan untuk mengambil user dari database dan mengisi `request.user`. Token tidak perlu disimpan dalam tabel session karena validitasnya dapat diperiksa dari tanda tangan dan claim yang terdapat di dalam token.

## 2. Risiko memercayai field reporter dari payload

Jika frontend bebas mengirim `"reporter": 5`, penyerang dapat mengganti ID tersebut menjadi ID pengguna lain atau admin. Akibatnya database mencatat laporan seolah-olah dibuat oleh orang lain. Kerentanan ini termasuk pemalsuan identitas/ownership dan dapat merusak audit trail serta aturan akses objek.

Pada implementasi yang aman, field reporter dibuat read-only dan tidak diambil dari payload. Setelah JWT berhasil divalidasi, DRF menyediakan user asli pada `self.request.user`. Method `perform_create()` kemudian memanggil `serializer.save(reporter=self.request.user)`. Dengan demikian identitas pelapor berasal dari token yang telah diverifikasi server, bukan dari angka yang dapat dimanipulasi klien.

## 3. Perbedaan has_permission() dan has_object_permission()

`has_permission()` dijalankan lebih awal ketika DRF memeriksa apakah request secara umum boleh memasuki view. Pada tahap ini DRF belum mengambil satu objek Report tertentu, sehingga fungsi hanya memiliki konteks request dan view. Contohnya adalah memeriksa apakah user sudah login atau apakah user memiliki role Citizen.

`has_object_permission()` dijalankan setelah view mengambil objek tertentu melalui `get_object()`. Pada tahap ini parameter `obj` sudah tersedia, sehingga sistem dapat memeriksa `obj.reporter`, `obj.status`, atau atribut objek lainnya.

Pengecekan `obj.status == 'DRAFT'` tidak dapat diletakkan di `has_permission()` karena variabel `obj` belum ada. Jika dipaksakan, program akan mengalami error karena belum ada baris Report spesifik yang sedang diperiksa. Pemeriksaan tersebut tepat diletakkan pada `has_object_permission()`.

## 4. Workflow frontend ketika access token kedaluwarsa

Frontend tidak boleh langsung menghapus isi form ketika menerima `401 Unauthorized`. Data laporan yang sedang diketik harus tetap berada di state aplikasi atau penyimpanan sementara. Frontend lalu mengirim refresh token ke endpoint `/api/token/refresh/`. Jika refresh token masih valid, server mengembalikan access token baru. Frontend menyimpan access token baru, memasangnya pada header Authorization, kemudian mengulangi request POST laporan dengan payload yang sama. Karena isi form tetap dipertahankan, pengguna tidak kehilangan laporan dan tidak perlu login kembali.

Apabila refresh token juga sudah kedaluwarsa atau tidak valid, barulah frontend meminta pengguna login kembali. Isi form sebaiknya tetap disimpan sementara agar dapat dikirim setelah proses login selesai.
