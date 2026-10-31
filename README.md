# Hotel Booking Demand – Interactive Dashboard

## Identitas
- Nama: AL ZAHRA NUR FEBRIAN
- NPM: 241051006
- Mata Kuliah: Visualisasi Data
- Dosen: Muryan Awaludin, S.Kom., M.Kom.

## Deskripsi
Dashboard interaktif untuk mengeksplorasi data pemesanan hotel, pembatalan, karakteristik pelanggan, dan harga kamar (ADR).

## Dataset
Kaggle – Hotel Booking Demand: https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand

Dataset asli umumnya berisi 119.390 baris. Jumlah setelah cleaning dapat berbeda karena baris tidak lengkap dan duplikasi dihapus.

## Fitur Dashboard
- 3 KPI: total pemesanan, tingkat pembatalan, dan rata-rata ADR.
- 4 visualisasi: tren pemesanan bulanan, proporsi pembatalan, pemesanan berdasarkan jenis hotel, dan hubungan lead time dengan ADR.
- 3 filter interaktif: jenis hotel, segmen pasar, dan tahun kedatangan.
- Insight otomatis dihitung berdasarkan data yang sedang difilter.
- Tabel data pemesanan (maksimal 1.000 baris ditampilkan).
- Kategori `Undefined`/kosong tidak dipakai untuk menentukan segmen pasar dengan pembatalan tertinggi. Insight segmen hanya menghitung kategori valid dengan minimal 100 pemesanan agar tidak menyesatkan.

## Struktur Folder
```text
Hotel_Booking_UTS_Fixed/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── hotel_bookings.csv  (letakkan dataset Kaggle di sini)
└── scripts/
    └── clean_data.py
```

## Cara Menjalankan di Windows
1. Unduh dataset dari Kaggle dan ekstrak file `hotel_bookings.csv`.
2. Letakkan `hotel_bookings.csv` ke folder `data`.
3. Buka folder proyek, klik address bar File Explorer, ketik `cmd`, lalu tekan Enter.
4. Jalankan perintah berikut satu per satu:

```bash
python -m pip install -r requirements.txt
python scripts/clean_data.py
streamlit run app.py
```

5. Browser akan membuka dashboard di alamat lokal yang ditampilkan terminal, biasanya `http://localhost:8501`.

## Deploy ke Streamlit Community Cloud
1. Upload seluruh isi folder proyek ke repository GitHub Public.
2. Buka https://share.streamlit.io/ dan login dengan GitHub.
3. Pilih **Create app**, lalu pilih repository dan branch.
4. Isi lokasi file utama dengan `app.py`, lalu klik **Deploy**.
5. Simpan URL dashboard yang diberikan Streamlit untuk dikumpulkan.

## Catatan Analisis
Jangan menuliskan temuan yang belum diperiksa. Setelah dashboard dijalankan, catat nilai KPI dan insight yang tampil sesuai filter awal. ADR adalah Average Daily Rate atau rata-rata tarif kamar per hari.
