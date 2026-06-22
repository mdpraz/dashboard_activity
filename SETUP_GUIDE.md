# Panduan Setup — Agent Activity Dashboard (Streamlit)

Dashboard ini membaca data langsung dari Google Sheet (publish-as-CSV), jadi kamu tinggal **update Google Sheet tiap hari** dan dashboard otomatis ikut berubah (refresh tiap 5 menit, atau klik tombol "Refresh data" di sidebar untuk instan).

---

## 1. Siapkan Google Sheet

1. Buat Google Sheet baru, beri nama misalnya `Agent Activity Data`.
2. Buat 1 sheet/tab berisi data mentah dengan kolom **persis** seperti ini (urutan bebas, nama kolom harus sama):

   ```
   grass_date | team_id | product_key | teleid | calls | contacts |
   contact_duration | hours_work | leads_assign | start_call | end_call |
   calls_0810 | calls_1012 | calls_1214 | calls_1416 | calls_1618
   ```

   Sebagai referensi format, ada file `sample_data_for_google_sheet.csv` di paket ini — bisa kamu import langsung ke Google Sheet (**File → Import → Upload**) sebagai starting point, lalu tinggal lanjutkan update harian dari situ.

3. Setiap hari, copy-paste baris baru dari Excel harian kamu ke bagian bawah sheet ini (append, bukan replace) — sama seperti cara kerja kamu sekarang.

---

## 2. Publish Sheet sebagai CSV Link

1. Di Google Sheet, klik **File → Share → Publish to web**.
2. Di dropdown pertama, pilih **sheet/tab yang berisi data** (bukan "Entire Document" kalau ada beberapa tab).
3. Di dropdown kedua, pilih format **Comma-separated values (.csv)**.
4. Klik **Publish**, konfirmasi.
5. Copy link yang muncul — bentuknya seperti:
   ```
   https://docs.google.com/spreadsheets/d/e/2PACX-xxxxxxxxxx/pub?gid=0&single=true&output=csv
   ```
   atau
   ```
   https://docs.google.com/spreadsheets/d/xxxxxxxxxx/pub?output=csv
   ```

⚠️ **Catatan:** Setelah publish, isi sheet itu bisa diakses siapa saja yang punya link (read-only). Jangan masukkan data sensitif/PII di luar yang memang perlu ditampilkan di dashboard publik.

---

## 3. Push Project ke GitHub

1. Buat repo baru di GitHub, misalnya `agent-activity-dashboard`.
2. Upload semua file di folder ini (`app.py`, `requirements.txt`, `.gitignore`) ke repo tersebut.
   - **JANGAN** upload `.streamlit/secrets.toml` (file asli) — itu rahasia. Yang di-upload cukup `.streamlit/secrets.toml.example` sebagai referensi.
3. Commit & push.

```bash
git init
git add app.py requirements.txt .gitignore .streamlit/secrets.toml.example
git commit -m "Initial agent activity dashboard"
git branch -M main
git remote add origin https://github.com/USERNAME/agent-activity-dashboard.git
git push -u origin main
```

---

## 4. Deploy ke Streamlit Community Cloud

1. Buka [share.streamlit.io](https://share.streamlit.io), login dengan akun GitHub kamu.
2. Klik **New app**.
3. Pilih repo `agent-activity-dashboard`, branch `main`, file utama `app.py`.
4. Sebelum deploy, klik **Advanced settings → Secrets**, lalu masukkan:
   ```toml
   SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/.../pub?output=csv"
   ```
   (pakai link CSV dari langkah 2)
5. Klik **Deploy**.
6. Tunggu beberapa menit — dashboard akan live di link seperti:
   ```
   https://agent-activity-dashboard-xxxx.streamlit.app
   ```

Link ini yang bisa kamu bagikan ke siapa saja (publik, sesuai yang kamu mau).

---

## 5. Update Data Harian (Workflow Rutin)

Setelah setup awal selesai, rutinitas hariannya jadi simpel:

1. Buka file Excel `cek_activity` harian kamu.
2. Copy baris-baris baru (hari ini).
3. Paste ke baris paling bawah di Google Sheet yang sudah di-publish.
4. Tunggu maks. 5 menit (auto-refresh) atau buka dashboard lalu klik **🔄 Refresh data** di sidebar.
5. Dashboard otomatis menghitung ulang semua metrik (connect rate, talk hours, dll) dari data terbaru.

Tidak perlu deploy ulang, tidak perlu sentuh kode — sheet adalah satu-satunya yang perlu diupdate.

---

## 6. Update Kode di Masa Depan

Kalau nanti ada perubahan rumus/tampilan:
1. Edit `app.py` di lokal atau langsung di GitHub.
2. Push ke `main`.
3. Streamlit Cloud otomatis re-deploy dalam 1-2 menit.

---

## Troubleshooting

| Masalah | Kemungkinan Penyebab |
|---|---|
| "SHEET_CSV_URL belum diset" | Lupa isi Secrets di Streamlit Cloud settings |
| "Kolom berikut tidak ditemukan" | Nama kolom di Google Sheet tidak persis sama (cek typo/spasi) |
| Data tidak update setelah edit sheet | Cache 5 menit — klik tombol Refresh, atau tunggu |
| Link CSV menampilkan halaman HTML, bukan data | Salah pilih format saat Publish to web — pastikan pilih CSV, bukan "Web page" |
| Sheet publish tapi tetap error 404 | Coba publish ulang, kadang link generate baru perlu beberapa menit aktif |
