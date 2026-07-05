"""
01_load_preprocessing.py
=========================
Tahap 1: Load Data & Preprocessing
- Load data penjualan WiFi dari file Excel
- Konversi kolom 'month' menjadi datetime
- Agregasi total revenue per bulan (groupby month)
- Set 'month' sebagai index time series

Output:
- monthly_revenue.csv (data agregasi bulanan yang siap dipakai
  pada tahap analisis & modeling selanjutnya)
"""

import pandas as pd

# ── 1. Load data ──────────────────────────────────────────────────────────
INPUT_FILE = "dataset_wifi_with_total.xlsx"

df = pd.read_excel(INPUT_FILE)
print("Data berhasil di-load.")
print("Jumlah baris :", len(df))
print("Kolom        :", df.columns.tolist())
print(df.head())

# ── 2. Konversi kolom 'month' menjadi datetime ──────────────────────────────
df["month"] = pd.to_datetime(df["month"])

# ── 3. Agregasi total revenue per bulan ─────────────────────────────────────
monthly = df.groupby("month")["revenue"].sum().reset_index()

# ── 4. Set 'month' sebagai index, dan pastikan frekuensi bulanan (MS) ───────
monthly = monthly.set_index("month").asfreq("MS")
monthly.sort_index(inplace=True)

print("\n=== Data Revenue Bulanan (Agregasi) ===")
print(monthly)

# ── 5. Simpan hasil untuk dipakai di tahap berikutnya ───────────────────────
OUTPUT_FILE = "monthly_revenue.csv"
monthly.to_csv(OUTPUT_FILE)
print(f"\nData agregasi bulanan disimpan ke: {OUTPUT_FILE}")
