"""
app.py
========
Dashboard Analisis Penjualan WiFi (Streamlit + Plotly)

Cara menjalankan:
    streamlit run app.py

Pastikan file-file berikut ada di folder yang sama:
    - dataset_wifi_with_total.xlsx
    - forecast_precomputed.csv
    - fitted_precomputed.csv
    - mape_value.txt
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────────────────────────────────
# PAGE CONFIG & GLOBAL STYLE
# ─────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WiFi Sales Dashboard",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

PRIMARY = "#6C5CE7"     # ungu
SECONDARY = "#4F8BFF"   # biru
ACCENT = "#00CEC9"
BG_CARD = "#1A1C29"
BG_APP = "#0B0D14"
TEXT_LIGHT = "#E6E6F0"
TEXT_MUTED = "#9295AF"
BORDER = "#2A2D3E"

CUSTOM_CSS = f"""
<style>
    /* ── Import modern font ─────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    /* ── App background: subtle gradient instead of flat white ────────── */
    .stApp {{
        background: radial-gradient(circle at top left, #161A2C 0%, {BG_APP} 45%, #0A0B12 100%);
        color: {TEXT_LIGHT};
    }}

    /* ── Main content spacing ───────────────────────────────────────── */
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 1300px;
    }}

    /* ── Sidebar ─────────────────────────────────────────────────────── */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #181B2C 0%, #11121C 100%);
        border-right: 1px solid {BORDER};
    }}
    [data-testid="stSidebar"] .block-container {{
        padding-top: 1.5rem;
        padding-left: 1.2rem;
        padding-right: 1.2rem;
    }}

    /* ── Sidebar radio menu (acts like nav tabs) ────────────────────── */
    [data-testid="stSidebar"] [role="radiogroup"] label {{
        background: rgba(255,255,255,0.02);
        border: 1px solid transparent;
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 6px;
        transition: all 0.18s ease;
        width: 100%;
    }}
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {{
        background: rgba(108,92,231,0.14);
        border-color: rgba(108,92,231,0.35);
        transform: translateX(2px);
    }}
    [data-testid="stSidebar"] [role="radiogroup"] label p {{
        font-weight: 600;
        font-size: 0.95rem;
    }}

    /* ── Metric cards ────────────────────────────────────────────────── */
    [data-testid="stMetric"] {{
        background: linear-gradient(135deg, {BG_CARD} 0%, #20233A 100%);
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 20px 18px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.35), 0 1px 0 rgba(255,255,255,0.04) inset;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }}
    [data-testid="stMetric"]:hover {{
        transform: translateY(-3px);
        border-color: rgba(108,92,231,0.45);
        box-shadow: 0 12px 30px rgba(108,92,231,0.20), 0 1px 0 rgba(255,255,255,0.06) inset;
    }}
    [data-testid="stMetricLabel"] {{
        color: {TEXT_MUTED} !important;
        font-weight: 600;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}
    [data-testid="stMetricValue"] {{
        color: {TEXT_LIGHT} !important;
        font-size: 1.7rem !important;
        font-weight: 700 !important;
    }}
    [data-testid="stMetricDelta"] {{
        font-weight: 600;
    }}

    /* ── Generic card container ─────────────────────────────────────── */
    .block-card {{
        background: linear-gradient(135deg, {BG_CARD} 0%, #1E2136 100%);
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 24px 26px;
        margin-bottom: 22px;
        box-shadow: 0 10px 28px rgba(0,0,0,0.30), 0 1px 0 rgba(255,255,255,0.03) inset;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }}
    .block-card:hover {{
        border-color: rgba(108,92,231,0.30);
        box-shadow: 0 12px 32px rgba(0,0,0,0.38), 0 1px 0 rgba(255,255,255,0.05) inset;
    }}
    .block-card h4, .block-card h3 {{
        margin-top: 0;
        margin-bottom: 14px;
    }}

    /* ── Typography ──────────────────────────────────────────────────── */
    h1, h2, h3, h4, h5 {{
        color: {TEXT_LIGHT} !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em;
    }}
    p, span, label, .stMarkdown {{
        color: {TEXT_LIGHT};
    }}
    .stCaption, [data-testid="stCaptionContainer"] {{
        color: {TEXT_MUTED} !important;
    }}

    .gradient-title {{
        background: linear-gradient(90deg, {PRIMARY}, {SECONDARY} 60%, {ACCENT});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        padding-bottom: 4px;
    }}

    /* ── Insight boxes ───────────────────────────────────────────────── */
    .insight-box {{
        background: linear-gradient(135deg, rgba(108,92,231,0.10), rgba(79,139,255,0.07));
        border: 1px solid rgba(108,92,231,0.18);
        border-left: 4px solid {PRIMARY};
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
        color: {TEXT_LIGHT};
        line-height: 1.6;
        box-shadow: 0 4px 14px rgba(0,0,0,0.18);
        transition: transform 0.15s ease, border-color 0.15s ease;
    }}
    .insight-box:hover {{
        transform: translateX(3px);
        border-left-color: {ACCENT};
    }}

    /* ── Badges / pills ──────────────────────────────────────────────── */
    .badge {{
        display: inline-block;
        background: linear-gradient(90deg, {PRIMARY}, {SECONDARY});
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        margin-right: 8px;
        margin-bottom: 6px;
        box-shadow: 0 2px 8px rgba(108,92,231,0.35);
    }}

    /* ── Buttons ─────────────────────────────────────────────────────── */
    .stButton > button, .stDownloadButton > button {{
        background: linear-gradient(90deg, {PRIMARY}, {SECONDARY});
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.55em 1.4em;
        font-weight: 600;
        box-shadow: 0 4px 14px rgba(108,92,231,0.30);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .stButton > button:hover, .stDownloadButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(108,92,231,0.40);
        color: white;
    }}

    /* ── Inputs: multiselect, selectbox, dataframe ──────────────────── */
    [data-baseweb="select"], [data-baseweb="popover"] {{
        border-radius: 10px !important;
    }}
    [data-testid="stDataFrame"] {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid {BORDER};
    }}

    /* ── Divider ─────────────────────────────────────────────────────── */
    hr {{
        border-color: {BORDER} !important;
        margin: 1.4rem 0 !important;
    }}

    /* ── Top banner / hero header ───────────────────────────────────── */
    .top-banner {{
        background: linear-gradient(120deg, rgba(108,92,231,0.18), rgba(79,139,255,0.10) 60%, rgba(0,206,201,0.08));
        border: 1px solid rgba(108,92,231,0.25);
        border-radius: 18px;
        padding: 22px 28px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.30);
    }}
    .top-banner p {{
        color: {TEXT_MUTED};
        margin: 4px 0 0 0;
        font-size: 0.95rem;
    }}

    /* ── Scrollbar polish ───────────────────────────────────────────── */
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: {BG_APP}; }}
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, {PRIMARY}, {SECONDARY});
        border-radius: 8px;
    }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Plotly color sequences & template
PLOTLY_COLORWAY = [SECONDARY, PRIMARY, ACCENT, "#FD79A8", "#74B9FF", "#A29BFE", "#55EFC4"]
PLOTLY_TEMPLATE = "plotly_dark"


def style_fig(fig, height=420):
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        colorway=PLOTLY_COLORWAY,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_LIGHT, family="Inter, sans-serif"),
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, x=0)
    )
    fig.update_xaxes(showgrid=True, gridcolor="#2A2D3E")
    fig.update_yaxes(showgrid=True, gridcolor="#2A2D3E")
    return fig


# ─────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("dataset_wifi_with_total.xlsx")
    df["month"] = pd.to_datetime(df["month"])
    return df


@st.cache_data
def load_forecast():
    forecast_df = pd.read_csv("forecast_precomputed.csv", parse_dates=["month"])
    fitted_df = pd.read_csv("fitted_precomputed.csv", parse_dates=["month"])
    with open("mape_value.txt") as f:
        mape = float(f.read().strip())
    return forecast_df, fitted_df, mape


df = load_data()
forecast_df, fitted_df, mape = load_forecast()

# ─────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<h2 class='gradient-title'>📡 WiFi Analytics</h2>",
        unsafe_allow_html=True
    )
    st.caption("Dashboard Analisis & Forecasting Penjualan WiFi")
    st.markdown("---")

    menu = st.radio(
        "📂 Menu",
        ["🏠 Overview", "🔍 EDA", "📈 Forecasting", "💡 Insight"],
        label_visibility="visible"
    )

    st.markdown("---")
    st.markdown("**🎯 Filter Data**")

    area_options = sorted(df["area"].unique().tolist())
    package_options = sorted(df["package"].unique().tolist())

    selected_areas = st.multiselect("🌍 Area", area_options, default=area_options)
    selected_packages = st.multiselect("📦 Paket WiFi", package_options, default=package_options)

    st.markdown("---")
    st.caption("Dibuat untuk Tugas Akhir D3 - Informatika | Data Science")

# Filtered dataframe
if not selected_areas:
    selected_areas = area_options
if not selected_packages:
    selected_packages = package_options

fdf = df[df["area"].isin(selected_areas) & df["package"].isin(selected_packages)]

if fdf.empty:
    st.warning("⚠️ Tidak ada data untuk kombinasi filter yang dipilih. Menampilkan semua data.")
    fdf = df.copy()

monthly_fdf = fdf.groupby("month").agg(
    revenue=("revenue", "sum"),
    new_customers=("new_customers", "sum"),
    churn_customers=("churn_customers", "sum"),
    total_customers=("total_customers", "sum")
).reset_index().sort_values("month")


# ═════════════════════════════════════════════════════════════════════════
# PAGE 1: OVERVIEW
# ═════════════════════════════════════════════════════════════════════════
if menu == "🏠 Overview":
    st.markdown(
        "<div class='top-banner'><h1 class='gradient-title' style='margin:0'>🏠 Overview Penjualan WiFi</h1>"
        "<p>Ringkasan performa bisnis berdasarkan data & filter yang dipilih</p></div>",
        unsafe_allow_html=True
    )

    total_revenue = monthly_fdf["revenue"].sum()
    total_new_customers = monthly_fdf["new_customers"].sum()
    total_churn = monthly_fdf["churn_customers"].sum()
    avg_total_customers = monthly_fdf["total_customers"].mean()

    if len(monthly_fdf) >= 2:
        growth = (monthly_fdf["revenue"].iloc[-1] - monthly_fdf["revenue"].iloc[0]) \
                 / monthly_fdf["revenue"].iloc[0] * 100
    else:
        growth = 0.0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Total Revenue", f"Rp {total_revenue/1e9:,.2f} B")
    with col2:
        st.metric("👥 Rata-rata Total Pelanggan", f"{avg_total_customers:,.0f}")
    with col3:
        st.metric("🆕 Total Pelanggan Baru", f"{total_new_customers:,.0f}")
    with col4:
        st.metric("📈 Growth Revenue", f"{growth:+.2f}%",
                  delta=f"{growth:+.2f}%")

    st.markdown("---")

    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown("<div class='block-card'>", unsafe_allow_html=True)
        st.markdown("#### 📊 Tren Revenue Bulanan")
        fig = px.area(
            monthly_fdf, x="month", y="revenue",
            labels={"month": "Bulan", "revenue": "Revenue (Rp)"}
        )
        fig.update_traces(line=dict(color=SECONDARY, width=3),
                           fillcolor="rgba(108,92,231,0.18)")
        fig = style_fig(fig, height=380)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown("<div class='block-card'>", unsafe_allow_html=True)
        st.markdown("#### 🥧 Komposisi Revenue per Paket")
        pkg_rev = fdf.groupby("package")["revenue"].sum().reset_index()
        fig2 = px.pie(pkg_rev, names="package", values="revenue", hole=0.45)
        fig2.update_traces(textposition="inside", textinfo="percent+label")
        fig2 = style_fig(fig2, height=380)
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='block-card'>", unsafe_allow_html=True)
    st.markdown("#### 📥 Download Data")
    csv_data = fdf.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Data (CSV)",
        data=csv_data,
        file_name="wifi_sales_filtered.csv",
        mime="text/csv"
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════
# PAGE 2: EDA
# ═════════════════════════════════════════════════════════════════════════
elif menu == "🔍 EDA":
    st.markdown(
        "<div class='top-banner'><h1 class='gradient-title' style='margin:0'>🔍 Exploratory Data Analysis</h1>"
        "<p>Eksplorasi tren revenue berdasarkan waktu, area, dan paket</p></div>",
        unsafe_allow_html=True
    )

    st.markdown("<div class='block-card'>", unsafe_allow_html=True)
    st.markdown("#### 📈 Tren Revenue per Bulan")
    fig = px.line(
        monthly_fdf, x="month", y="revenue", markers=True,
        labels={"month": "Bulan", "revenue": "Revenue (Rp)"}
    )
    fig.update_traces(line=dict(color=SECONDARY, width=3), marker=dict(size=8, color=PRIMARY))
    fig = style_fig(fig)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='block-card'>", unsafe_allow_html=True)
        st.markdown("#### 🌍 Revenue per Area (Top 15)")
        area_rev = fdf.groupby("area")["revenue"].sum().sort_values(ascending=False).head(15).reset_index()
        fig = px.bar(
            area_rev, x="revenue", y="area", orientation="h",
            labels={"revenue": "Revenue (Rp)", "area": "Area"},
            color="revenue", color_continuous_scale=[SECONDARY, PRIMARY]
        )
        fig.update_layout(yaxis=dict(autorange="reversed"))
        fig = style_fig(fig, height=480)
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='block-card'>", unsafe_allow_html=True)
        st.markdown("#### 📦 Revenue per Paket WiFi")
        pkg_rev = fdf.groupby("package")["revenue"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(
            pkg_rev, x="package", y="revenue",
            labels={"package": "Paket", "revenue": "Revenue (Rp)"},
            color="package", color_discrete_sequence=PLOTLY_COLORWAY
        )
        fig = style_fig(fig, height=480)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='block-card'>", unsafe_allow_html=True)
    st.markdown("#### 👥 New vs Churn Customers per Bulan")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly_fdf["month"], y=monthly_fdf["new_customers"],
        mode="lines+markers", name="New Customers",
        line=dict(color=ACCENT, width=3)
    ))
    fig.add_trace(go.Scatter(
        x=monthly_fdf["month"], y=monthly_fdf["churn_customers"],
        mode="lines+markers", name="Churn Customers",
        line=dict(color="#FD79A8", width=3, dash="dash")
    ))
    fig = style_fig(fig)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════
# PAGE 3: FORECASTING
# ═════════════════════════════════════════════════════════════════════════
elif menu == "📈 Forecasting":
    st.markdown(
        "<div class='top-banner'><h1 class='gradient-title' style='margin:0'>📈 Forecasting Revenue (SARIMA)</h1>"
        "<p>Prediksi revenue 6 bulan ke depan menggunakan model SARIMA (data nasional - tidak terpengaruh filter)</p></div>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 MAPE Model", f"{mape:.2f}%")
    with col2:
        st.metric("🔮 Forecast Bulan Depan", f"Rp {forecast_df['forecast_revenue'].iloc[0]/1e9:.2f} B")
    with col3:
        st.metric("📅 Periode Forecast", f"{len(forecast_df)} Bulan")

    st.markdown("<div class='block-card'>", unsafe_allow_html=True)
    st.markdown("#### 📊 Actual vs Predicted Revenue")

    actual_monthly = df.groupby("month")["revenue"].sum().reset_index().sort_values("month")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=actual_monthly["month"], y=actual_monthly["revenue"],
        mode="lines+markers", name="Actual Revenue",
        line=dict(color=SECONDARY, width=3)
    ))
    fig.add_trace(go.Scatter(
        x=fitted_df["month"], y=fitted_df["fitted_revenue"],
        mode="lines+markers", name="Fitted (Model)",
        line=dict(color=ACCENT, width=2, dash="dot")
    ))
    fig.add_trace(go.Scatter(
        x=forecast_df["month"], y=forecast_df["forecast_revenue"],
        mode="lines+markers", name="Forecast 6 Bulan",
        line=dict(color=PRIMARY, width=3, dash="dash"),
        marker=dict(size=9, symbol="diamond")
    ))
    fig.add_trace(go.Scatter(
        x=pd.concat([forecast_df["month"], forecast_df["month"][::-1]]),
        y=pd.concat([forecast_df["upper_95"], forecast_df["lower_95"][::-1]]),
        fill="toself", fillcolor="rgba(108,92,231,0.15)",
        line=dict(color="rgba(255,255,255,0)"),
        name="95% Confidence Interval", showlegend=True
    ))
    fig = style_fig(fig, height=480)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='block-card'>", unsafe_allow_html=True)
    st.markdown("#### 📋 Tabel Hasil Forecast")
    display_df = forecast_df.copy()
    display_df.columns = ["Bulan", "Prediksi Revenue", "Batas Bawah (95%)", "Batas Atas (95%)"]
    display_df["Bulan"] = display_df["Bulan"].dt.strftime("%B %Y")
    for c in display_df.columns[1:]:
        display_df[c] = display_df[c].apply(lambda x: f"Rp {x:,.0f}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    csv_forecast = forecast_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Forecast (CSV)",
        data=csv_forecast,
        file_name="forecast_wifi_6bulan.csv",
        mime="text/csv"
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════
# PAGE 4: INSIGHT
# ═════════════════════════════════════════════════════════════════════════
elif menu == "💡 Insight":
    st.markdown(
        "<div class='top-banner'><h1 class='gradient-title' style='margin:0'>💡 Insight Bisnis Otomatis</h1>"
        "<p>Analisis otomatis berdasarkan data revenue, pelanggan baru, dan churn</p></div>",
        unsafe_allow_html=True
    )

    # ── Hitung insight secara dinamis dari data terfilter ──
    monthly_all = df.groupby("month").agg(
        revenue=("revenue", "sum"),
        new_customers=("new_customers", "sum"),
        churn_customers=("churn_customers", "sum")
    ).reset_index().sort_values("month")

    growth_all = (monthly_all["revenue"].iloc[-1] - monthly_all["revenue"].iloc[0]) \
                  / monthly_all["revenue"].iloc[0] * 100

    area_rev_all = df.groupby("area")["revenue"].sum().sort_values(ascending=False)
    best_area = area_rev_all.index[0]
    worst_area = area_rev_all.index[-1]

    pkg_rev_all = df.groupby("package")["revenue"].sum().sort_values(ascending=False)
    pkg_new_all = df.groupby("package")["new_customers"].sum().sort_values(ascending=False)
    best_pkg_revenue = pkg_rev_all.index[0]
    best_pkg_volume = pkg_new_all.index[0]

    # Korelasi churn vs revenue (exclude Jan karena anomali outlier)
    clean = monthly_all[monthly_all["month"] != monthly_all["month"].min()]
    corr_churn = clean["churn_customers"].corr(clean["revenue"])

    next_forecast = forecast_df["forecast_revenue"].iloc[0]

    st.markdown(f"""
    <div class='insight-box'>
        <span class='badge'>📊 TREN</span>
        Revenue tumbuh <b>{growth_all:+.2f}%</b> dari bulan pertama ke bulan terakhir data.
        Tren relatif <b>stabil</b> dengan fluktuasi bulanan yang kecil.
    </div>

    <div class='insight-box'>
        <span class='badge'>🌍 AREA TERBAIK</span>
        <b>{best_area}</b> adalah area dengan revenue tertinggi (Rp {area_rev_all.iloc[0]/1e6:,.1f} Juta),
        sedangkan <b>{worst_area}</b> memiliki revenue terendah (Rp {area_rev_all.iloc[-1]/1e6:,.1f} Juta).
    </div>

    <div class='insight-box'>
        <span class='badge'>📦 PAKET TERLARIS</span>
        Paket <b>{best_pkg_revenue}</b> menyumbang revenue terbesar (Rp {pkg_rev_all.iloc[0]/1e9:,.2f} M),
        sementara paket <b>{best_pkg_volume}</b> paling banyak diminati pelanggan baru
        ({pkg_new_all.iloc[0]:,} pelanggan).
    </div>

    <div class='insight-box'>
        <span class='badge'>🔁 CHURN vs REVENUE</span>
        Korelasi antara churn pelanggan dan revenue bulanan adalah <b>{corr_churn:.2f}</b>.
        {"Churn cenderung bergerak searah dengan revenue, mengindikasikan churn rate yang relatif konstan dan diimbangi pelanggan baru." if corr_churn > 0 else "Churn berkorelasi negatif dengan revenue, mengindikasikan churn berdampak pada penurunan pendapatan."}
    </div>

    <div class='insight-box'>
        <span class='badge'>🔮 PREDIKSI</span>
        Model SARIMA memprediksi revenue bulan depan sekitar <b>Rp {next_forecast/1e9:,.2f} Miliar</b>
        dengan akurasi model (MAPE) <b>{mape:.2f}%</b>. Tren 6 bulan ke depan diperkirakan
        <b>stabil/cenderung mendatar</b>.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ✅ Rekomendasi Bisnis")

    rec_col1, rec_col2 = st.columns(2)
    with rec_col1:
        st.markdown("""
        <div class='block-card'>
        <b>🎯 Retensi Pelanggan</b><br>
        Tekan churn rate melalui program loyalitas, diskon perpanjangan,
        dan peningkatan kualitas layanan agar basis pelanggan tumbuh, bukan stagnan.
        </div>
        <div class='block-card'>
        <b>📦 Strategi Upsell</b><br>
        Dorong migrasi pelanggan dari paket entry-level ke paket menengah
        (100-300 Mbps) untuk meningkatkan margin tanpa kehilangan volume.
        </div>
        """, unsafe_allow_html=True)

    with rec_col2:
        st.markdown(f"""
        <div class='block-card'>
        <b>🌍 Replikasi Area Top Performer</b><br>
        Pelajari faktor sukses di <b>{best_area}</b> dan terapkan strategi
        serupa pada area dengan revenue rendah seperti <b>{worst_area}</b>.
        </div>
        <div class='block-card'>
        <b>📈 Target Pertumbuhan</b><br>
        Gunakan hasil forecast SARIMA sebagai baseline, lalu tetapkan target
        pertumbuhan inkremental (10-15% YoY) melalui kombinasi strategi akuisisi & retensi.
        </div>
        """, unsafe_allow_html=True)
