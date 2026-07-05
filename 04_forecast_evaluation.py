"""
04_forecast_evaluation.py
===========================
Tahap 4: Forecasting, Evaluasi, & Visualisasi
- Prediksi revenue 6 bulan ke depan
- Membuat dataframe hasil prediksi (forecast_df)
- Menghitung MAPE (Mean Absolute Percentage Error)
- Plot perbandingan actual vs predicted revenue

Input:
- monthly_revenue.csv (hasil dari 01_load_preprocessing.py)
- model_sarima.pkl    (hasil dari 03_sarima_modeling.py)

Output:
- forecast_wifi_6bulan.csv  (dataframe hasil prediksi 6 bulan ke depan)
- sarima_forecast_wifi.png  (grafik actual vs fitted & forecast)
- Nilai MAPE ditampilkan di console
"""

import pandas as pd
import numpy as np
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings
warnings.filterwarnings("ignore")

# ── 1. Load data & model ────────────────────────────────────────────────────
monthly = pd.read_csv("monthly_revenue.csv", index_col="month", parse_dates=True)
monthly = monthly.asfreq("MS")

model = joblib.load("model_sarima.pkl")

# ── 2. Hitung nilai fitted (in-sample) untuk evaluasi MAPE ──────────────────
fitted = model.predict_in_sample()
actual = monthly["revenue"].values

mape = np.mean(np.abs((actual - fitted) / actual)) * 100
print(f"=== Evaluasi Model ===")
print(f"MAPE (In-Sample) = {mape:.2f}%")

# ── 3. Forecast 6 bulan ke depan ────────────────────────────────────────────
N_FORECAST = 6

forecast, conf_int = model.predict(n_periods=N_FORECAST, return_conf_int=True)

last_date = monthly.index[-1]
forecast_index = pd.date_range(
    start=last_date + pd.DateOffset(months=1),
    periods=N_FORECAST,
    freq="MS"
)

forecast_df = pd.DataFrame({
    "month": forecast_index,
    "forecast_revenue": forecast.round(0).astype(int),
    "lower_95": conf_int[:, 0].round(0).astype(int),
    "upper_95": conf_int[:, 1].round(0).astype(int)
}).set_index("month")

print("\n=== Dataframe Hasil Forecast (6 Bulan ke Depan) ===")
print(forecast_df)

# Simpan dataframe forecast
forecast_df.to_csv("forecast_wifi_6bulan.csv")
print("\nDataframe forecast disimpan ke: forecast_wifi_6bulan.csv")

# ── 4. Visualisasi: Actual vs Predicted ─────────────────────────────────────
fig, axes = plt.subplots(2, 1, figsize=(12, 9))

# -- Panel atas: Actual vs Fitted (in-sample) --------------------------------
ax1 = axes[0]
ax1.plot(monthly.index, monthly["revenue"],
         marker="o", linewidth=2, color="#1f77b4", label="Actual Revenue")
ax1.plot(monthly.index, fitted,
         marker="x", linestyle="--", linewidth=2, color="#ff7f0e", label="Predicted (Fitted)")
ax1.set_title("Actual vs Predicted Revenue (In-Sample)", fontsize=12, fontweight="bold")
ax1.set_xlabel("Bulan")
ax1.set_ylabel("Revenue (Rp)")
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Rp {x/1e9:.2f}B"))
ax1.grid(True, linestyle="--", alpha=0.5)
ax1.legend()
ax1.text(0.99, 0.92, f"MAPE = {mape:.2f}%",
         transform=ax1.transAxes, ha="right", va="top", fontsize=10,
         bbox=dict(boxstyle="round,pad=0.4", facecolor="#e8f5e9", edgecolor="green"))

# -- Panel bawah: Actual + Forecast 6 bulan ----------------------------------
ax2 = axes[1]
ax2.plot(monthly.index, monthly["revenue"],
         marker="o", linewidth=2, color="#1f77b4", label="Actual Revenue")
ax2.plot(forecast_df.index, forecast_df["forecast_revenue"],
         marker="s", linestyle="--", linewidth=2, color="#d62728", label="Forecast 6 Bulan")
ax2.fill_between(forecast_df.index,
                 forecast_df["lower_95"], forecast_df["upper_95"],
                 alpha=0.2, color="#d62728", label="95% Confidence Interval")
ax2.axvline(monthly.index[-1], color="gray", linestyle=":", linewidth=1.5)
ax2.set_title("Revenue Forecast - 6 Bulan ke Depan", fontsize=12, fontweight="bold")
ax2.set_xlabel("Bulan")
ax2.set_ylabel("Revenue (Rp)")
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Rp {x/1e9:.2f}B"))
ax2.grid(True, linestyle="--", alpha=0.5)
ax2.legend()

plt.tight_layout()
plt.savefig("sarima_forecast_wifi.png", dpi=150, bbox_inches="tight")
plt.close()
print("Grafik actual vs predicted disimpan ke: sarima_forecast_wifi.png")
