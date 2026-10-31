from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
source_file = DATA_DIR / "hotel_bookings.csv"
output_file = DATA_DIR / "hotel_bookings_clean.csv"

if not source_file.exists():
    raise FileNotFoundError(
        "File hotel_bookings.csv belum ditemukan. Simpan dataset Kaggle "
        "ke dalam folder data terlebih dahulu."
    )

print("Membaca dataset...")
df = pd.read_csv(source_file, low_memory=False)
df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]
rows_before = len(df)

# Isi nilai kosong pada kolom kategori dan jumlah anak.
if "country" in df.columns:
    df["country"] = df["country"].fillna("Unknown")
if "market_segment" in df.columns:
    df["market_segment"] = df["market_segment"].fillna("Unknown")
if "customer_type" in df.columns:
    df["customer_type"] = df["customer_type"].fillna("Unknown")
if "children" in df.columns:
    df["children"] = pd.to_numeric(df["children"], errors="coerce").fillna(0)

numeric_columns = [
    "is_canceled", "lead_time", "arrival_date_year", "arrival_date_week_number",
    "arrival_date_day_of_month", "stays_in_weekend_nights", "stays_in_week_nights",
    "adults", "children", "babies", "previous_cancellations",
    "previous_bookings_not_canceled", "booking_changes", "agent", "company",
    "days_in_waiting_list", "adr", "required_car_parking_spaces",
    "total_of_special_requests",
]
for column in numeric_columns:
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

# Hapus baris tanpa informasi inti untuk analisis dashboard.
core_columns = [
    "hotel", "is_canceled", "arrival_date_year", "arrival_date_month", "adr"
]
missing_core = [column for column in core_columns if column not in df.columns]
if missing_core:
    raise ValueError("Kolom inti tidak ditemukan: " + ", ".join(missing_core))

before_core_filter = len(df)
df = df.dropna(subset=core_columns).copy()
removed_incomplete = before_core_filter - len(df)

before_dedup = len(df)
df = df.drop_duplicates().copy()
removed_duplicates = before_dedup - len(df)

df.to_csv(output_file, index=False)
print(f"Baris awal: {rows_before:,}")
print(f"Baris tanpa data inti yang dihapus: {removed_incomplete:,}")
print(f"Duplikat yang dihapus: {removed_duplicates:,}")
print(f"Baris akhir: {len(df):,}")
print(f"Dataset bersih tersimpan di: {output_file}")
