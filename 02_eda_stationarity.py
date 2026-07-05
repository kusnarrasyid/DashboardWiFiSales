"""
02_eda_stationarity.py
========================
Tahap 2: Exploratory Data Analysis (EDA) & Uji Stasioneritas
- Plot tren revenue bulanan
- Uji stasioneritas dengan Augmented Dickey-Fuller (ADF) Test

Input:
- monthly_revenue.csv (hasil dari 01_load_preprocessing.py)

Output:
- plot_trend_revenue.png (grafik tren revenue bulanan)
- Hasil ADF test ditampilkan di console
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from statsmodels.tsa.stattools import adfuller

# ── 1. Load data hasil preprocessing ────────────────────────────────────────
monthly = pd.read_csv("monthly_revenue.csv", index_col="month", parse_dates=True)
monthly = monthly.asfreq("MS")

print("=== Data Revenue Bulanan ===")
print(monthly)

# ── 2. Plot Tren Revenue Bulanan ────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(monthly.index, monthly["revenue"],
        marker="o", linewidth=2, color="#1f77b4", label="Revenue Bulanan")
ax.set_title("Tren Revenue Penjualan WiFi per Bulan", fontsize=13, fontweight="bold")
ax.set_xlabel("Bulan")
ax.set_ylabel("Revenue (Rp)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Rp {x/1e9:.2f}B"))
ax.grid(True, linestyle="--", alpha=0.5)
ax.legend()

plt.tight_layout()
plt.savefig("plot_trend_revenue.png", dpi=150, bbox_inches="tight")
plt.close()
print("\nGrafik tren revenue disimpan ke: plot_trend_revenue.png")

# ── 3. Uji Stasioneritas (ADF Test) ─────────────────────────────────────────
adf_result = adfuller(monthly["revenue"])

print("\n=== Augmented Dickey-Fuller (ADF) Test ===")
print(f"ADF Statistic : {adf_result[0]:.4f}")
print(f"p-value       : {adf_result[1]:.4f}")
print("Critical Values:")
for key, value in adf_result[4].items():
    print(f"   {key} : {value:.4f}")

if adf_result[1] < 0.05:
    print("\nKesimpulan: Data STASIONER (p-value < 0.05) -> d = 0")
else:
    print("\nKesimpulan: Data TIDAK STASIONER (p-value >= 0.05) -> perlu differencing (d >= 1)")
