# Balikin 🔍

**Balikin** adalah sebuah platform digital terpusat yang dirancang khusus untuk mengatasi permasalahan pelaporan dan pencarian barang hilang di lingkungan kampus Institut Pertanian Bogor (IPB). Sistem ini menggantikan metode pelaporan informal (seperti grup WhatsApp atau platform X) menjadi sistem yang lebih terstruktur, terdokumentasi, dan mudah diakses oleh seluruh civitas akademik.


## 👥 Aktor Sistem
Sistem ini dirancang dengan arsitektur peran (Role-based):
1. **Pencari (Mahasiswa/Civitas)**: Dapat membuat laporan barang hilang, melihat daftar barang hilang, dan melacak status laporannya.
2. **Petugas Keamanan (Security)**: Bertugas menginput barang yang ditemukan, memverifikasi laporan, dan memproses pengembalian barang ke pemiliknya.
3. **Admin**: Memantau seluruh sistem, mengelola pengguna (User Management), dan melihat log aktivitas sistem.

## 💻 Tech Stack
Sistem ini dibangun menggunakan arsitektur modern Client-Server:
- **Frontend**: React.js, TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python), SQLAlchemy, Pydantic, Alembic
- **Database**: PostgreSQL
- **Security**: JWT Authentication, Bcrypt Password Hashing

## 🛠️ Prasyarat (Prerequisites)
Pastikan Anda sudah menginstal aplikasi berikut sebelum menjalankan proyek:
- **Node.js** (v16 atau ke atas)
- **Python** (v3.10 atau ke atas)
- **PostgreSQL** (pastikan server berjalan di lokal Anda)
