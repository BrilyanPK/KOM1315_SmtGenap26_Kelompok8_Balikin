# Balikin 🔍

**Balikin** adalah sebuah platform digital terpusat yang dirancang khusus untuk mengatasi permasalahan pelaporan dan pencarian barang hilang di lingkungan kampus Institut Pertanian Bogor (IPB). Sistem ini menggantikan metode pelaporan informal (seperti grup WhatsApp atau platform X) menjadi sistem yang lebih terstruktur, terdokumentasi, dan mudah diakses oleh seluruh civitas akademik.
> 🔗 **Source Code Lengkap:** Kunjungi repositori utama proyek di [**BrilyanPK/IPB-Lost-Found**](https://github.com/BrilyanPK/IPB-Lost-Found)

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

---

## ⚡ Instalasi Singkat (Quick Start)
Jika Anda ingin mencoba menjalankan sistem Balikin secara lokal untuk menguji fitur keamanannya, ikuti langkah berikut:

### 1. Clone Repositori Utama
```bash
git clone https://github.com/BrilyanPK/IPB-Lost-Found.git
cd IPB-Lost-Found
```
*(Pastikan Anda telah membuat database kosong bernama `lostfound_db` di PostgreSQL Anda)*

### 2. Jalankan Peladen (Backend)
Buka terminal dan masuk ke folder `backend`:
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate  # (Gunakan 'source venv/bin/activate' untuk Mac/Linux)
pip install -r requirements.txt
python seed.py          # Mengisi data dummy (Admin, Petugas, Pencari)
uvicorn app.main:app --reload
```

### 3. Jalankan Antarmuka (Frontend)
Buka terminal baru dan masuk ke folder `frontend`:
```bash
cd frontend
npm install
npm run dev
```
Akses aplikasi melalui peramban di `http://localhost:5173`.

---
