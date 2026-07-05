"""
05_business_insight.py
========================
Tahap 5: Insight Bisnis Otomatis
- Analisis tren penjualan (naik/turun)
- Area dengan performa terbaik
- Paket WiFi paling laku
- Pengaruh churn terhadap revenue
- Proyeksi kondisi 1 tahun ke depan (berdasarkan forecast SARIMA)

Input:
- dataset_wifi_with_total.xlsx (data mentah)
- forecast_wifi_6bulan.csv     (hasil dari 04_forecast_evaluation.py)

Output:
- business_insight_charts.png  (grafik insight: tren, area, paket, new vs churn)
- business_insight_summary.txt (ringkasan insight + rekomendasi bisnis)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ── 1. Load data ─────────────────────────────────────────────────────────
df = pd.read_excel("dataset_wifi_with_total.xlsx")
df["month"] = pd.to_datetime(df["month"])

monthly = df.groupby("month").agg(
    revenue=("revenue", "sum"),
    new_customers=("new_customers", "sum"),
    churn_customers=("churn_customers", "sum")
).reset_index().sort_values("month")

# ── 2. Analisis Tren Penjualan ──────────────────────────────────────────────
growth = (monthly["revenue"].iloc[-1] - monthly["revenue"].iloc[0]) \
         / monthly["revenue"].iloc[0] * 100
avg_revenue = monthly["revenue"].mean()
cov_revenue = monthly["revenue"].std() / avg_revenue * 100
trend_label = "naik" if growth > 0 else "turun"

# ── 3. Area dengan Performa Terbaik ─────────────────────────────────────────
area_rev = df.groupby("area")["revenue"].sum().sort_values(ascending=False)
area_new = df.groupby("area")["new_customers"].sum().sort_values(ascending=False)
best_area = area_rev.index[0]
worst_area = area_rev.index[-1]

# ── 4. Paket WiFi Paling Laku ───────────────────────────────────────────────
pkg_rev = df.groupby("package")["revenue"].sum().sort_values(ascending=False)
pkg_new = df.groupby("package")["new_customers"].sum().sort_values(ascending=False)
best_pkg_revenue = pkg_rev.index[0]
best_pkg_volume = pkg_new.index[0]

# ── 5. Pengaruh Churn terhadap Revenue ──────────────────────────────────────
# Bulan pertama (Januari) dikecualikan karena nilai churn_customers
# pada bulan tersebut merupakan anomali/outlier dibanding bulan lain.
clean = monthly.iloc[1:]
corr_churn_revenue = clean["churn_customers"].corr(clean["revenue"])
corr_new_revenue = clean["new_customers"].corr(clean["revenue"])

total_new = df["new_customers"].sum()
total_churn = df["churn_customers"].sum()

# ── 6. Proyeksi 1 Tahun ke Depan (dari hasil forecast SARIMA) ───────────────
try:
    forecast_df = pd.read_csv("forecast_wifi_6bulan.csv", parse_dates=["month"])
    forecast_total_6m = forecast_df["forecast_revenue"].sum()
    forecast_avg = forecast_df["forecast_revenue"].mean()
    # Proyeksi sederhana 12 bulan: asumsikan 6 bulan kedua mengikuti
    # rata-rata bulan terakhir forecast (karena model memprediksi
    # kondisi mendatar / flat untuk horizon menengah)
    proj_12m_total = forecast_total_6m + forecast_avg * 6
    has_forecast = True
except FileNotFoundError:
    has_forecast = False

# ── 7. Visualisasi Insight ───────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# (a) Tren revenue bulanan
ax = axes[0, 0]
ax.plot(monthly["month"], monthly["revenue"], marker="o", color="#1f77b4", lw=2)
ax.set_title("Tren Total Revenue Bulanan", fontweight="bold")
ax.set_xlabel("Bulan")
ax.set_ylabel("Revenue (Rp)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Rp{x/1e9:.2f}B"))
ax.grid(alpha=0.3, linestyle="--")
ax.tick_params(axis="x", rotation=45)

# (b) Top 10 area berdasarkan revenue
ax = axes[0, 1]
top10 = area_rev.head(10)
ax.barh(top10.index[::-1], top10.values[::-1], color="#2ca02c")
ax.set_title("Top 10 Area Berdasarkan Revenue", fontweight="bold")
ax.set_xlabel("Revenue (Rp)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Rp{x/1e6:.0f}M"))

# (c) Revenue per paket
ax = axes[1, 0]
ax.bar(pkg_rev.index, pkg_rev.values, color="#ff7f0e")
ax.set_title("Total Revenue per Paket WiFi", fontweight="bold")
ax.set_xlabel("Paket")
ax.set_ylabel("Revenue (Rp)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Rp{x/1e9:.1f}B"))
ax.tick_params(axis="x", rotation=30)

# (d) New vs churn customers per bulan
ax = axes[1, 1]
ax.plot(monthly["month"], monthly["new_customers"], marker="o",
        color="#2ca02c", label="New Customers")
ax.plot(monthly["month"].iloc[1:], monthly["churn_customers"].iloc[1:], marker="x",
        color="#d62728", label="Churn Customers")
ax.set_title("New vs Churn Customers per Bulan\n(Bulan pertama dikecualikan - outlier data)",
              fontweight="bold")
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Pelanggan")
ax.legend()
ax.grid(alpha=0.3, linestyle="--")
ax.tick_params(axis="x", rotation=45)

plt.tight_layout()
plt.savefig("business_insight_charts.png", dpi=150, bbox_inches="tight")
plt.close()
print("Grafik insight disimpan ke: business_insight_charts.png")

# ── 8. Ringkasan Insight (teks) ─────────────────────────────────────────────
churn_relation = (
    "Churn cenderung bergerak SEARAH dengan revenue (korelasi positif). "
    "Hal ini terjadi karena churn rate relatif konstan setiap bulan dan "
    "jumlah pelanggan baru (yang berkorelasi sangat kuat dengan revenue) "
    "mendominasi pengaruh terhadap revenue. Net pelanggan (new - churn) "
    "hampir selalu mendekati nol, menunjukkan kondisi 'replacement "
    "equilibrium' - pelanggan keluar diimbangi pelanggan baru."
    if corr_churn_revenue > 0 else
    "Churn berkorelasi NEGATIF dengan revenue, artinya kenaikan churn "
    "cenderung diikuti penurunan revenue secara langsung."
)

summary_lines = []
summary_lines.append("=" * 70)
summary_lines.append("RINGKASAN INSIGHT BISNIS - PENJUALAN WIFI")
summary_lines.append("=" * 70)

summary_lines.append("\n1. TREN PENJUALAN")
summary_lines.append(f"   - Revenue {trend_label} sebesar {growth:.2f}% dari bulan pertama")
summary_lines.append(f"     ke bulan terakhir data.")
summary_lines.append(f"   - Rata-rata revenue per bulan: Rp {avg_revenue:,.0f}")
summary_lines.append(f"   - Variasi (CoV) antar bulan: {cov_revenue:.2f}% (relatif stabil)")

summary_lines.append("\n2. AREA DENGAN PERFORMA TERBAIK")
summary_lines.append(f"   - Area dengan revenue tertinggi : {best_area} "
                      f"(Rp {area_rev.iloc[0]:,.0f})")
summary_lines.append(f"   - Area dengan revenue terendah  : {worst_area} "
                      f"(Rp {area_rev.iloc[-1]:,.0f})")
summary_lines.append(f"   - Area dengan pelanggan baru terbanyak: {area_new.index[0]} "
                      f"({area_new.iloc[0]:,} pelanggan)")

summary_lines.append("\n3. PAKET WIFI PALING LAKU")
summary_lines.append(f"   - Revenue tertinggi  : Paket {best_pkg_revenue} "
                      f"(Rp {pkg_rev.iloc[0]:,.0f})")
summary_lines.append(f"   - Pelanggan baru terbanyak: Paket {best_pkg_volume} "
                      f"({pkg_new.iloc[0]:,} pelanggan)")
summary_lines.append("   - Interpretasi: paket entry-level menjadi volume driver,")
summary_lines.append("     sedangkan paket premium menjadi margin driver.")

summary_lines.append("\n4. PENGARUH CHURN TERHADAP REVENUE")
summary_lines.append(f"   - Korelasi churn vs revenue   : {corr_churn_revenue:.3f}")
summary_lines.append(f"   - Korelasi new_cust vs revenue: {corr_new_revenue:.3f}")
summary_lines.append(f"   - Total pelanggan baru (1 tahun): {total_new:,}")
summary_lines.append(f"   - Total churn (1 tahun)         : {total_churn:,.0f}")
summary_lines.append(f"   - {churn_relation}")

summary_lines.append("\n5. PREDIKSI KONDISI 1 TAHUN KE DEPAN")
if has_forecast:
    summary_lines.append(f"   - Rata-rata forecast revenue (6 bulan ke depan): "
                          f"Rp {forecast_avg:,.0f}/bulan")
    summary_lines.append(f"   - Total forecast 6 bulan ke depan: Rp {forecast_total_6m:,.0f}")
    summary_lines.append(f"   - Estimasi proyeksi total 12 bulan ke depan: "
                          f"Rp {proj_12m_total:,.0f}")
    summary_lines.append("   - Model SARIMA memprediksi kondisi revenue relatif STABIL/FLAT,")
    summary_lines.append("     tanpa lonjakan atau penurunan signifikan jika tidak ada")
    summary_lines.append("     intervensi bisnis baru.")
else:
    summary_lines.append("   - File forecast_wifi_6bulan.csv tidak ditemukan.")
    summary_lines.append("     Jalankan 04_forecast_evaluation.py terlebih dahulu.")

summary_lines.append("\n" + "=" * 70)
summary_lines.append("REKOMENDASI BISNIS")
summary_lines.append("=" * 70)
summary_lines.append("1. Tekan churn rate melalui program retensi, diskon perpanjangan,")
summary_lines.append("   dan peningkatan kualitas layanan, karena pertumbuhan pelanggan")
summary_lines.append("   baru saat ini hanya menutupi pelanggan yang keluar.")
summary_lines.append("2. Dorong upsell dari paket entry-level ke paket menengah")
summary_lines.append("   (100-300 Mbps) untuk meningkatkan margin tanpa kehilangan")
summary_lines.append("   basis pelanggan.")
summary_lines.append(f"3. Replikasi strategi area top performer ({best_area}) ke area")
summary_lines.append(f"   dengan performa rendah seperti {worst_area}.")
summary_lines.append("4. Tingkatkan akuisisi pelanggan baru di kota besar yang masih")
summary_lines.append("   memiliki revenue relatif rendah dibanding potensi pasarnya.")
summary_lines.append("5. Gunakan hasil forecast SARIMA sebagai baseline target, lalu")
summary_lines.append("   tetapkan target pertumbuhan inkremental (10-15% YoY) melalui")
summary_lines.append("   kombinasi strategi retensi dan akuisisi.")

summary_text = "\n".join(summary_lines)
print("\n" + summary_text)

with open("business_insight_summary.txt", "w", encoding="utf-8") as f:
    f.write(summary_text)

print("\nRingkasan insight disimpan ke: business_insight_summary.txt")
