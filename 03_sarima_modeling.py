"""
03_sarima_modeling.py
=======================
Tahap 3: Modeling SARIMA
- Menentukan parameter (p,d,q) dan (P,D,Q,s) menggunakan auto_arima
- Melatih (fit) model SARIMA terbaik berdasarkan data historis

Catatan:
- Data historis yang tersedia hanya 12 bulan (1 tahun), sehingga
  seasonal differencing (D) di-set tetap 0 (D=0) karena belum ada
  cukup periode (minimal 2 siklus musiman) untuk mengestimasi
  komponen seasonal secara penuh. Hal ini merupakan limitasi pada
  dataset dan dapat menjadi catatan untuk pengembangan penelitian
  selanjutnya (mengumpulkan data >= 24 bulan).

Input:
- monthly_revenue.csv (hasil dari 01_load_preprocessing.py)

Output:
- model_sarima.pkl (model SARIMA yang sudah di-fit, untuk dipakai
  pada tahap forecasting & evaluasi)
"""

import pandas as pd
import joblib
from pmdarima import auto_arima
import warnings
warnings.filterwarnings("ignore")

# ── 1. Load data hasil preprocessing ────────────────────────────────────────
monthly = pd.read_csv("monthly_revenue.csv", index_col="month", parse_dates=True)
monthly = monthly.asfreq("MS")

print("=== Data Revenue Bulanan ===")
print(monthly)

# ── 2. Auto ARIMA untuk menentukan parameter (p,d,q)(P,D,Q,s) ───────────────
print("\nMencari parameter SARIMA terbaik dengan auto_arima...")

model = auto_arima(
    monthly["revenue"],
    seasonal=True,
    m=12,          # periode musiman bulanan (12 bulan = 1 tahun)
    D=0,           # seasonal differencing di-fix 0 (data hanya 12 obs)
    d=None,        # non-seasonal differencing ditentukan otomatis
    trace=True,
    error_action="ignore",
    suppress_warnings=True,
    stepwise=True
)

print("\n=== Ringkasan Model SARIMA Terbaik ===")
print(model.summary())

order = model.order
seasonal_order = model.seasonal_order
print(f"\nParameter (p,d,q)       : {order}")
print(f"Parameter (P,D,Q,s)      : {seasonal_order}")

# ── 3. Simpan model untuk digunakan pada tahap forecasting ──────────────────
joblib.dump(model, "model_sarima.pkl")
print("\nModel SARIMA disimpan ke: model_sarima.pkl")
