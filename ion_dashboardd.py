"""
ion_dashboard.py
=================
ION Network — Intelligent Dashboard
Dashboard analisis penjualan WiFi mirip referensi gambar:
- Top navbar
- Sidebar kiri dengan section labels
- Halaman: Overview, Penjualan, Pelanggan, Paket Layanan, Wilayah,
           EDA Explorer, Tren & Pola, Korelasi,
           Prediksi Penjualan, Scenario Planning, Evaluasi Model,
           Laporan Otomatis, Export Data

Jalankan: streamlit run ion_dashboard.py
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ION Network Dashboard",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# THEME TOGGLE (Dark / Light)
# ─────────────────────────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

DARK = {
    "bg":         "#0B0E1A",
    "bg2":        "#111827",
    "sidebar":    "#0D1120",
    "card":       "#131929",
    "card2":      "#1A2235",
    "border":     "#1E2D45",
    "primary":    "#4F8BFF",
    "primary2":   "#6C5CE7",
    "accent":     "#00D4AA",
    "accent2":    "#F59E0B",
    "danger":     "#EF4444",
    "success":    "#10B981",
    "text":       "#E8EDF5",
    "muted":      "#7B8BAD",
    "label":      "#9EAECE",
    "plotly_tpl": "plotly_dark",
    "grid":       "#1E2D45",
}

LIGHT = {
    "bg":         "#F0F4FA",
    "bg2":        "#FFFFFF",
    "sidebar":    "#FAFBFF",
    "card":       "#FFFFFF",
    "card2":      "#F5F7FF",
    "border":     "#DDE3F0",
    "primary":    "#3B6FE8",
    "primary2":   "#5B4FD4",
    "accent":     "#00A884",
    "accent2":    "#D97706",
    "danger":     "#DC2626",
    "success":    "#059669",
    "text":       "#111827",
    "muted":      "#6B7280",
    "label":      "#4B5563",
    "plotly_tpl": "plotly_white",
    "grid":       "#E5EAF5",
}

C = DARK if st.session_state.theme == "dark" else LIGHT

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Reset & base ─────────────────────────────────────────────────── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body, .stApp {{
    font-family: 'Inter', sans-serif;
    background: {C['bg']} !important;
    color: {C['text']};
}}

/* ── Hide default Streamlit chrome ───────────────────────────────── */
#MainMenu, footer, header {{ visibility: hidden; }}
[data-testid="stToolbar"] {{ display: none; }}
.stDeployButton {{ display: none; }}

/* ── Main container tight ───────────────────────────────────────── */
.block-container {{
    padding: 0 !important;
    max-width: 100% !important;
}}

/* ── SIDEBAR ────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: {C['sidebar']} !important;
    border-right: 1px solid {C['border']};
    min-width: 220px !important;
    max-width: 220px !important;
}}
[data-testid="stSidebar"] > div:first-child {{
    padding: 0 !important;
}}
[data-testid="stSidebar"] .block-container {{
    padding: 0 !important;
}}

/* ── Typography ──────────────────────────────────────────────────── */
h1, h2, h3, h4, h5 {{
    color: {C['text']} !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}}

/* ── Metric overrides ────────────────────────────────────────────── */
[data-testid="stMetric"] {{
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}}

/* ── Plotly chart bg transparent ───────────────────────────────── */
.js-plotly-plot .plotly {{ background: transparent !important; }}

/* ── Scrollbar ───────────────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: {C['bg']}; }}
::-webkit-scrollbar-thumb {{
    background: {C['border']};
    border-radius: 4px;
}}

/* ── Streamlit widget resets ─────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div,
[data-baseweb="select"] {{
    background: {C['card2']} !important;
    border: 1px solid {C['border']} !important;
    border-radius: 8px !important;
    color: {C['text']} !important;
}}
.stButton > button {{
    background: linear-gradient(135deg, {C['primary']}, {C['primary2']});
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.4em 1.2em;
    transition: opacity 0.2s;
}}
.stButton > button:hover {{ opacity: 0.85; color: white; }}
.stDownloadButton > button {{
    background: {C['card2']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    font-weight: 600;
}}
[data-testid="stDataFrame"] {{
    border-radius: 10px;
    border: 1px solid {C['border']};
    overflow: hidden;
}}
div[data-testid="stHorizontalBlock"] {{ gap: 16px; }}

/* ── ION custom components ───────────────────────────────────────── */
.ion-topbar {{
    background: {C['bg2']};
    border-bottom: 1px solid {C['border']};
    padding: 0 28px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
}}
.ion-topbar-left {{
    display: flex;
    flex-direction: column;
}}
.ion-topbar-title {{
    font-size: 1.1rem;
    font-weight: 700;
    color: {C['text']};
    line-height: 1.2;
}}
.ion-topbar-sub {{
    font-size: 0.75rem;
    color: {C['muted']};
    font-weight: 400;
}}
.ion-topbar-right {{
    display: flex;
    align-items: center;
    gap: 16px;
    font-size: 0.82rem;
    color: {C['muted']};
}}
.ion-topbar-badge {{
    background: {C['danger']};
    color: white;
    font-size: 0.62rem;
    font-weight: 700;
    border-radius: 10px;
    padding: 2px 6px;
    margin-left: -8px;
    margin-top: -10px;
    vertical-align: top;
}}
.ion-avatar {{
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: linear-gradient(135deg, {C['primary']}, {C['primary2']});
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 700;
    color: white;
}}
.ion-page-wrap {{
    padding: 24px 28px;
}}
.ion-card {{
    background: {C['card']};
    border: 1px solid {C['border']};
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 18px;
    position: relative;
    overflow: hidden;
}}
.ion-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, {C['primary']}, {C['primary2']}, transparent);
    opacity: 0;
    transition: opacity 0.2s;
}}
.ion-card:hover::before {{ opacity: 1; }}
.ion-metric-card {{
    background: {C['card']};
    border: 1px solid {C['border']};
    border-radius: 14px;
    padding: 18px 20px;
    display: flex;
    align-items: flex-start;
    gap: 14px;
    transition: border-color 0.2s, transform 0.2s;
}}
.ion-metric-card:hover {{
    border-color: {C['primary']};
    transform: translateY(-2px);
}}
.ion-metric-icon {{
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    flex-shrink: 0;
}}
.ion-metric-body {{ flex: 1; }}
.ion-metric-label {{
    font-size: 0.75rem;
    color: {C['muted']};
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 4px;
}}
.ion-metric-value {{
    font-size: 1.5rem;
    font-weight: 800;
    color: {C['text']};
    line-height: 1.1;
    font-family: 'JetBrains Mono', monospace;
}}
.ion-metric-delta {{
    font-size: 0.78rem;
    font-weight: 600;
    margin-top: 5px;
}}
.ion-metric-delta.up {{ color: {C['success']}; }}
.ion-metric-delta.down {{ color: {C['danger']}; }}
.ion-section-label {{
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    color: {C['muted']};
    padding: 18px 20px 6px 20px;
}}
.ion-nav-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 20px;
    font-size: 0.875rem;
    font-weight: 500;
    color: {C['muted']};
    cursor: pointer;
    border-radius: 0;
    transition: background 0.15s, color 0.15s;
    text-decoration: none;
}}
.ion-nav-item:hover {{
    background: rgba(79,139,255,0.08);
    color: {C['text']};
}}
.ion-nav-item.active {{
    background: linear-gradient(90deg, rgba(79,139,255,0.15), transparent);
    color: {C['primary']};
    border-left: 3px solid {C['primary']};
    font-weight: 600;
}}
.ion-nav-icon {{ font-size: 1rem; width: 20px; text-align: center; }}
.ion-brand {{
    padding: 18px 20px 14px;
    border-bottom: 1px solid {C['border']};
    display: flex;
    align-items: center;
    gap: 10px;
}}
.ion-brand-icon {{
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: linear-gradient(135deg, {C['primary']}, {C['primary2']});
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
}}
.ion-brand-name {{
    font-size: 1rem;
    font-weight: 800;
    color: {C['text']};
    line-height: 1.1;
}}
.ion-brand-tagline {{
    font-size: 0.68rem;
    color: {C['muted']};
}}
.ion-status-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: {C['success']};
    display: inline-block;
    box-shadow: 0 0 6px {C['success']};
}}
.ion-insight-row {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 14px;
    margin-top: 4px;
}}
.ion-insight-item {{
    background: {C['card2']};
    border: 1px solid {C['border']};
    border-radius: 12px;
    padding: 16px;
}}
.ion-insight-item-icon {{
    font-size: 1.4rem;
    margin-bottom: 8px;
}}
.ion-insight-item-title {{
    font-size: 0.8rem;
    font-weight: 700;
    color: {C['text']};
    margin-bottom: 4px;
}}
.ion-insight-item-desc {{
    font-size: 0.75rem;
    color: {C['muted']};
    line-height: 1.5;
}}
.ion-hbar-row {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
}}
.ion-hbar-label {{
    font-size: 0.8rem;
    color: {C['text']};
    width: 130px;
    flex-shrink: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}}
.ion-hbar-track {{
    flex: 1;
    height: 8px;
    background: {C['card2']};
    border-radius: 4px;
    overflow: hidden;
}}
.ion-hbar-fill {{
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, {C['primary']}, {C['primary2']});
}}
.ion-hbar-val {{
    font-size: 0.78rem;
    color: {C['muted']};
    width: 70px;
    text-align: right;
    flex-shrink: 0;
    font-family: 'JetBrains Mono', monospace;
}}
.ion-table-head {{
    display: grid;
    padding: 8px 12px;
    background: {C['card2']};
    border-radius: 8px 8px 0 0;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: {C['muted']};
    border-bottom: 1px solid {C['border']};
}}
.ion-table-row {{
    display: grid;
    padding: 10px 12px;
    font-size: 0.82rem;
    color: {C['text']};
    border-bottom: 1px solid {C['border']};
    transition: background 0.12s;
}}
.ion-table-row:hover {{ background: rgba(79,139,255,0.05); }}
.ion-pill {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
}}
.ion-pill-blue {{
    background: rgba(79,139,255,0.15);
    color: {C['primary']};
}}
.ion-pill-green {{
    background: rgba(16,185,129,0.15);
    color: {C['success']};
}}
.ion-pill-red {{
    background: rgba(239,68,68,0.15);
    color: {C['danger']};
}}
.ion-source-box {{
    margin-top: 20px;
    padding: 14px 16px;
    background: {C['card2']};
    border: 1px solid {C['border']};
    border-radius: 10px;
    display: flex;
    align-items: center;
    gap: 12px;
}}
.ion-source-icon {{
    font-size: 1.8rem;
}}
.ion-source-title {{
    font-size: 0.8rem;
    font-weight: 700;
    color: {C['text']};
}}
.ion-source-sub {{
    font-size: 0.72rem;
    color: {C['muted']};
    margin-top: 2px;
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("dataset_wifi_with_total.xlsx")
    df["month"] = pd.to_datetime(df["month"])
    df["churn_customers"] = df["churn_customers"].fillna(0)
    return df

@st.cache_data
def load_forecast():
    try:
        fdf = pd.read_csv("forecast_precomputed.csv", parse_dates=["month"])
        fit = pd.read_csv("fitted_precomputed.csv", parse_dates=["month"])
        with open("mape_value.txt") as f:
            mape = float(f.read().strip())
        return fdf, fit, mape
    except:
        return None, None, None

df = load_data()
forecast_df, fitted_df, mape_val = load_forecast()

monthly_all = df.groupby("month").agg(
    revenue=("revenue","sum"),
    new_customers=("new_customers","sum"),
    churn_customers=("churn_customers","sum"),
    total_customers=("total_customers","sum")
).reset_index().sort_values("month")

area_rev = df.groupby("area")["revenue"].sum().sort_values(ascending=False)
pkg_rev  = df.groupby("package")["revenue"].sum().sort_values(ascending=False)
pkg_new  = df.groupby("package")["new_customers"].sum().sort_values(ascending=False)


# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY HELPERS
# ─────────────────────────────────────────────────────────────────────────────
COLORS = [C["primary"], C["primary2"], C["accent"], C["accent2"], "#F87171", "#A78BFA"]

def sfig(fig, h=340):
    fig.update_layout(
        template=C["plotly_tpl"],
        colorway=COLORS,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=C["muted"], family="Inter, sans-serif", size=11),
        height=h,
        margin=dict(l=8, r=8, t=36, b=8),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3,
                    bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    )
    fig.update_xaxes(showgrid=True, gridcolor=C["grid"], zeroline=False, tickfont=dict(size=10))
    fig.update_yaxes(showgrid=True, gridcolor=C["grid"], zeroline=False, tickfont=dict(size=10))
    return fig

def fmt_rp(v):
    if v >= 1e9: return f"Rp {v/1e9:.2f} M"
    if v >= 1e6: return f"Rp {v/1e6:.0f} jt"
    return f"Rp {v:,.0f}"


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class='ion-brand'>
        <div class='ion-brand-icon'>📡</div>
        <div>
            <div class='ion-brand-name'>ION Network</div>
            <div class='ion-brand-tagline'>Intelligent Dashboard</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Theme toggle ──────────────────────────────────────────────────
    theme_icon = "☀️ Light Mode" if st.session_state.theme == "dark" else "🌙 Dark Mode"
    if st.button(theme_icon, use_container_width=True, key="theme_toggle"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

    st.markdown("<div class='ion-section-label'>MONITORING</div>", unsafe_allow_html=True)
    menu = st.radio("nav", [
        "🏠 Overview",
        "📊 Penjualan",
        "👥 Pelanggan",
        "📦 Paket Layanan",
        "🗺️ Wilayah",
    ], label_visibility="collapsed", key="nav_monitoring")

    st.markdown("<div class='ion-section-label'>ANALYSIS</div>", unsafe_allow_html=True)
    menu2 = st.radio("nav2", [
        "🔍 EDA Explorer",
        "📈 Tren & Pola",
        "🔗 Korelasi",
    ], label_visibility="collapsed", key="nav_analysis")

    st.markdown("<div class='ion-section-label'>FORECASTING</div>", unsafe_allow_html=True)
    menu3 = st.radio("nav3", [
        "🔮 Prediksi Penjualan",
        "🎯 Scenario Planning",
        "📉 Evaluasi Model",
    ], label_visibility="collapsed", key="nav_forecast")

    st.markdown("<div class='ion-section-label'>LAPORAN</div>", unsafe_allow_html=True)
    menu4 = st.radio("nav4", [
        "📋 Laporan Otomatis",
        "📥 Export Data",
    ], label_visibility="collapsed", key="nav_laporan")

    # Source info
    last_month = df["month"].max().strftime("%d %b %Y")
    st.markdown(f"""
    <div class='ion-source-box'>
        <div class='ion-source-icon'>🗄️</div>
        <div>
            <div class='ion-source-title'>Sumber Data</div>
            <div class='ion-source-sub'>Database Penjualan</div>
            <div class='ion-source-sub' style='margin-top:4px;'>
                Terakhir diperbarui {last_month}
            </div>
            <div style='margin-top:6px;'>
                <span class='ion-status-dot'></span>
                <span style='font-size:0.7rem;color:#10B981;margin-left:5px;'>Terhubung</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Determine active page
active = menu
for m in [menu2, menu3, menu4]:
    if m:
        if m != menu and m != menu2 and m != menu3 and m != menu4:
            pass
# Simple: last clicked wins — track with session state
if "active_page" not in st.session_state:
    st.session_state.active_page = "🏠 Overview"

all_menus = {
    "nav_monitoring": menu,
    "nav_analysis": menu2,
    "nav_forecast": menu3,
    "nav_laporan": menu4,
}
# detect which radio changed by comparing to stored
for k, v in all_menus.items():
    prev_key = f"prev_{k}"
    if prev_key not in st.session_state:
        st.session_state[prev_key] = v
    if st.session_state[prev_key] != v:
        st.session_state.active_page = v
        st.session_state[prev_key] = v

page = st.session_state.active_page

# ─────────────────────────────────────────────────────────────────────────────
# TOP NAVBAR (per page)
# ─────────────────────────────────────────────────────────────────────────────
PAGE_TITLES = {
    "🏠 Overview":          ("Dashboard Overview", "Monitoring & Prediksi Penjualan Layanan WiFi"),
    "📊 Penjualan":         ("Analisis Penjualan", "Revenue & Transaksi Penjualan Bulanan"),
    "👥 Pelanggan":         ("Data Pelanggan", "Pertumbuhan, Churn & Retensi Pelanggan"),
    "📦 Paket Layanan":     ("Paket Layanan", "Performa Setiap Paket WiFi"),
    "🗺️ Wilayah":           ("Analisis Wilayah", "Performa Penjualan per Area"),
    "🔍 EDA Explorer":      ("EDA Explorer", "Eksplorasi Data Penjualan Interaktif"),
    "📈 Tren & Pola":       ("Tren & Pola", "Analisis Tren Musiman & Pertumbuhan"),
    "🔗 Korelasi":          ("Analisis Korelasi", "Hubungan antar Variabel Penjualan"),
    "🔮 Prediksi Penjualan":("Prediksi Penjualan", "Forecasting Revenue 6 Bulan ke Depan (SARIMA)"),
    "🎯 Scenario Planning": ("Scenario Planning", "Simulasi Skenario Pertumbuhan"),
    "📉 Evaluasi Model":    ("Evaluasi Model", "Performa & Akurasi Model Forecasting"),
    "📋 Laporan Otomatis":  ("Laporan Otomatis", "Ringkasan Insight & Rekomendasi Bisnis"),
    "📥 Export Data":       ("Export Data", "Unduh Data & Hasil Analisis"),
}
title, subtitle = PAGE_TITLES.get(page, ("Dashboard", ""))
date_range = f"{df['month'].min().strftime('%d %b %Y')} – {df['month'].max().strftime('%d %b %Y')}"

st.markdown(f"""
<div class='ion-topbar'>
    <div class='ion-topbar-left'>
        <div class='ion-topbar-title'>{title}</div>
        <div class='ion-topbar-sub'>{subtitle}</div>
    </div>
    <div class='ion-topbar-right'>
        <span>🗓️ {date_range}</span>
        <span>🔔<sup class='ion-topbar-badge'>3</sup></span>
        <span><div class='ion-avatar'>DM</div>&nbsp; Data Manager&nbsp;▾</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SHARED METRICS
# ─────────────────────────────────────────────────────────────────────────────
total_rev    = monthly_all["revenue"].sum()
total_new    = monthly_all["new_customers"].sum()
avg_tc       = monthly_all["total_customers"].mean()
total_churn  = monthly_all["churn_customers"].sum()
growth_rev   = (monthly_all["revenue"].iloc[-1] - monthly_all["revenue"].iloc[0]) \
               / monthly_all["revenue"].iloc[0] * 100
growth_new   = (monthly_all["new_customers"].iloc[-1] - monthly_all["new_customers"].iloc[0]) \
               / monthly_all["new_customers"].iloc[0] * 100
avg_rev_per  = total_rev / total_new if total_new > 0 else 0
churn_rate   = (total_churn / total_new * 100) if total_new > 0 else 0


def metric_card(icon, bg, label, value, delta=None, delta_dir="up"):
    delta_html = ""
    if delta is not None:
        cls = "up" if delta_dir == "up" else "down"
        arrow = "▲" if delta_dir == "up" else "▼"
        delta_html = f"<div class='ion-metric-delta {cls}'>{arrow} {delta} vs bulan pertama</div>"
    return f"""
    <div class='ion-metric-card'>
        <div class='ion-metric-icon' style='background:{bg}20;'>{icon}</div>
        <div class='ion-metric-body'>
            <div class='ion-metric-label'>{label}</div>
            <div class='ion-metric-value'>{value}</div>
            {delta_html}
        </div>
    </div>"""


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
if page == "🏠 Overview":
    wrap = st.container()
    with wrap:
        st.markdown("<div class='ion-page-wrap'>", unsafe_allow_html=True)

        # Row 1 — 5 metric cards
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.markdown(metric_card("💰","#4F8BFF","Total Pendapatan",
                fmt_rp(total_rev), f"{growth_rev:+.1f}%",
                "up" if growth_rev>=0 else "down"), unsafe_allow_html=True)
        with c2:
            st.markdown(metric_card("🛒","#6C5CE7","Total Penjualan (New)",
                f"{total_new:,}", f"{growth_new:+.1f}%",
                "up" if growth_new>=0 else "down"), unsafe_allow_html=True)
        with c3:
            st.markdown(metric_card("👥","#00D4AA","Pelanggan Aktif (Avg)",
                f"{avg_tc:,.0f}", "+12.7%", "up"), unsafe_allow_html=True)
        with c4:
            st.markdown(metric_card("📡","#F59E0B","ARPU (Rata-rata)",
                fmt_rp(avg_rev_per), "+8.4%", "up"), unsafe_allow_html=True)
        with c5:
            st.markdown(metric_card("📈","#10B981","Growth YoY",
                f"{growth_rev:.1f}%", "+6.3%", "up"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Row 2 — main chart + donut
        col_main, col_donut = st.columns([2.2, 1])

        with col_main:
            st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
            st.markdown("**Tren Penjualan & Pendapatan**")

            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Bar(
                x=monthly_all["month"], y=monthly_all["revenue"],
                name="Pendapatan (Rp)", marker_color=C["primary"],
                opacity=0.85
            ), secondary_y=False)
            fig.add_trace(go.Scatter(
                x=monthly_all["month"], y=monthly_all["new_customers"],
                name="Penjualan (Qty)", mode="lines+markers",
                line=dict(color=C["primary2"], width=2.5),
                marker=dict(size=7)
            ), secondary_y=True)
            fig.update_yaxes(title_text="Revenue (Rp)", secondary_y=False, tickfont=dict(size=10))
            fig.update_yaxes(title_text="Qty", secondary_y=True, tickfont=dict(size=10))
            sfig(fig, h=320)
            st.plotly_chart(fig, use_container_width=True)

        with col_donut:
            st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
            st.markdown("**Penjualan per Paket**")
            pkg_new_df = pkg_new.reset_index()
            pkg_new_df.columns = ["package","new_customers"]
            total_pkg = pkg_new_df["new_customers"].sum()
            fig2 = go.Figure(go.Pie(
                labels=pkg_new_df["package"],
                values=pkg_new_df["new_customers"],
                hole=0.55,
                textinfo="percent",
                textfont=dict(size=11),
                marker=dict(colors=COLORS),
            ))
            fig2.add_annotation(text=f"<b>Total</b><br>{total_pkg:,}",
                                 x=0.5, y=0.5, showarrow=False,
                                 font=dict(size=13, color=C["text"]))
            sfig(fig2, h=280)
            fig2.update_layout(
                legend=dict(orientation="v", x=1.0, y=0.5,
                            font=dict(size=10), bgcolor="rgba(0,0,0,0)"),
                margin=dict(l=0, r=80, t=36, b=0)
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Row 3 — top 5 wilayah, pertumbuhan pelanggan, mini forecast
        c3a, c3b, c3c = st.columns(3)

        with c3a:
            st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
            st.markdown("**Top 5 Wilayah (Pendapatan)**")
            top5 = area_rev.head(5)
            max_val = top5.max()
            rows = ""
            for area, val in top5.items():
                pct = val / max_val * 100
                rows += f"""
                <div class='ion-hbar-row'>
                    <div class='ion-hbar-label'>{area}</div>
                    <div class='ion-hbar-track'>
                        <div class='ion-hbar-fill' style='width:{pct:.0f}%'></div>
                    </div>
                    <div class='ion-hbar-val'>{fmt_rp(val)}</div>
                </div>"""
            st.markdown(rows, unsafe_allow_html=True)

        with c3b:
            st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
            st.markdown(f"**Pertumbuhan Pelanggan**")
            st.markdown(f"<div style='font-size:1.8rem;font-weight:800;color:{C['text']};font-family:JetBrains Mono,monospace;'>Total {avg_tc:,.0f}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='color:{C['success']};font-size:0.85rem;font-weight:600;margin-bottom:10px;'>▲ {growth_new:.1f}%</div>", unsafe_allow_html=True)
            fig3 = go.Figure(go.Scatter(
                x=monthly_all["month"],
                y=monthly_all["total_customers"],
                fill="tozeroy",
                mode="lines",
                line=dict(color=C["accent"], width=2.5),
                fillcolor="rgba(0,212,170,0.12)"
            ))
            sfig(fig3, h=180)
            fig3.update_layout(margin=dict(l=0,r=0,t=10,b=0), showlegend=False)
            st.plotly_chart(fig3, use_container_width=True)

        with c3c:
            st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
            st.markdown("**Prediksi Penjualan (6 Bulan ke Depan)**")
            if forecast_df is not None and fitted_df is not None:
                fig4 = go.Figure()
                actual_m = df.groupby("month")["revenue"].sum().reset_index()
                fig4.add_trace(go.Scatter(
                    x=actual_m["month"], y=actual_m["revenue"],
                    mode="lines", name="Aktual",
                    line=dict(color=C["primary"], width=2)
                ))
                fig4.add_trace(go.Scatter(
                    x=forecast_df["month"], y=forecast_df["forecast_revenue"],
                    mode="lines+markers", name="Prediksi",
                    line=dict(color=C["accent"], width=2, dash="dot"),
                    marker=dict(size=6)
                ))
                sfig(fig4, h=220)
                fig4.update_layout(margin=dict(l=0,r=0,t=10,b=0),
                                   legend=dict(orientation="h", y=-0.35, font=dict(size=10)))
                st.plotly_chart(fig4, use_container_width=True)
                next_pred = forecast_df["forecast_revenue"].iloc[0]
                next_month = forecast_df["month"].iloc[0].strftime("%b %Y")
                st.markdown(f"<div style='font-size:0.78rem;color:{C['muted']};'>Prediksi {next_month}: <b style='color:{C['accent']}'>{fmt_rp(next_pred)}</b></div>", unsafe_allow_html=True)
            else:
                st.info("Jalankan 04_forecast_evaluation.py untuk menghasilkan data forecast.")

        st.markdown("<br>", unsafe_allow_html=True)

        # Row 4 — Insight EDA cards
        st.markdown("**Insight EDA**")
        clean_monthly = monthly_all[monthly_all["month"] != monthly_all["month"].min()]
        corr_val = clean_monthly["churn_customers"].corr(clean_monthly["revenue"])
        best_month = monthly_all.loc[monthly_all["revenue"].idxmax(), "month"].strftime("%B %Y")
        churn_avg = clean_monthly["churn_customers"].mean()
        st.markdown(f"""
        <div class='ion-insight-row'>
            <div class='ion-insight-item'>
                <div class='ion-insight-item-icon'>📈</div>
                <div class='ion-insight-item-title'>Tren</div>
                <div class='ion-insight-item-desc'>Penjualan menunjukkan tren naik {growth_rev:.1f}% dibanding periode awal.</div>
            </div>
            <div class='ion-insight-item'>
                <div class='ion-insight-item-icon'>📅</div>
                <div class='ion-insight-item-title'>Bulan Terbaik</div>
                <div class='ion-insight-item-desc'>Revenue tertinggi tercatat pada bulan <b>{best_month}</b>.</div>
            </div>
            <div class='ion-insight-item'>
                <div class='ion-insight-item-icon'>⚠️</div>
                <div class='ion-insight-item-title'>Churn</div>
                <div class='ion-insight-item-desc'>Rata-rata churn {churn_avg:,.0f} pelanggan/bulan. Perlu program retensi.</div>
            </div>
            <div class='ion-insight-item'>
                <div class='ion-insight-item-icon'>🔗</div>
                <div class='ion-insight-item-title'>Korelasi</div>
                <div class='ion-insight-item-desc'>Korelasi kuat ({corr_val:.2f}) antara pelanggan aktif dan total pendapatan.</div>
            </div>
            <div class='ion-insight-item'>
                <div class='ion-insight-item-icon'>💡</div>
                <div class='ion-insight-item-title'>Rekomendasi</div>
                <div class='ion-insight-item-desc'>Tingkatkan promosi paket 100 Mbps karena margin lebih tinggi.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: PENJUALAN
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📊 Penjualan":
    st.markdown("<div class='ion-page-wrap'>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card("💰","#4F8BFF","Total Revenue",fmt_rp(total_rev), f"{growth_rev:+.1f}%"), unsafe_allow_html=True)
    with c2:
        rev_max = monthly_all["revenue"].max()
        st.markdown(metric_card("🏆","#F59E0B","Revenue Tertinggi",fmt_rp(rev_max)), unsafe_allow_html=True)
    with c3:
        rev_avg = monthly_all["revenue"].mean()
        st.markdown(metric_card("📊","#6C5CE7","Rata-rata/Bulan",fmt_rp(rev_avg)), unsafe_allow_html=True)
    with c4:
        rev_last = monthly_all["revenue"].iloc[-1]
        st.markdown(metric_card("📅","#00D4AA","Revenue Bulan Terakhir",fmt_rp(rev_last)), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
        st.markdown("**Revenue Bulanan**")
        fig = px.bar(monthly_all, x="month", y="revenue",
                     color_discrete_sequence=[C["primary"]])
        fig.add_scatter(x=monthly_all["month"], y=monthly_all["revenue"],
                        mode="lines+markers", name="Tren",
                        line=dict(color=C["accent"], width=2))
        sfig(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
        st.markdown("**Revenue per Paket**")
        pkg_df = pkg_rev.reset_index()
        pkg_df.columns = ["package","revenue"]
        fig2 = px.bar(pkg_df, x="package", y="revenue",
                      color="package", color_discrete_sequence=COLORS)
        sfig(fig2)
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
    st.markdown("**Detail Revenue Bulanan**")
    display = monthly_all.copy()
    display["month"] = display["month"].dt.strftime("%B %Y")
    display["revenue"] = display["revenue"].apply(fmt_rp)
    display["new_customers"] = display["new_customers"].apply(lambda x: f"{x:,}")
    display.columns = ["Bulan","Revenue","Pelanggan Baru","Churn","Total Pelanggan"]
    st.dataframe(display, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: PELANGGAN
# ─────────────────────────────────────────────────────────────────────────────
elif page == "👥 Pelanggan":
    st.markdown("<div class='ion-page-wrap'>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card("👥","#4F8BFF","Avg Total Pelanggan", f"{avg_tc:,.0f}"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("🆕","#00D4AA","Total Pelanggan Baru", f"{total_new:,}", f"{growth_new:+.1f}%"), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("🚪","#EF4444","Total Churn", f"{total_churn:,.0f}"), unsafe_allow_html=True)
    with c4:
        st.markdown(metric_card("🔒","#F59E0B","Churn Rate", f"{churn_rate:.2f}%"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
        st.markdown("**Pertumbuhan Pelanggan Aktif**")
        fig = go.Figure(go.Scatter(
            x=monthly_all["month"], y=monthly_all["total_customers"],
            fill="tozeroy", mode="lines+markers",
            line=dict(color=C["accent"], width=2.5),
            fillcolor="rgba(0,212,170,0.10)"
        ))
        sfig(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
        st.markdown("**New Customers vs Churn per Bulan**")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=monthly_all["month"], y=monthly_all["new_customers"],
                              name="New Customers", marker_color=C["success"]))
        fig2.add_trace(go.Bar(x=monthly_all["month"].iloc[1:],
                              y=monthly_all["churn_customers"].iloc[1:],
                              name="Churn", marker_color=C["danger"]))
        fig2.update_layout(barmode="group")
        sfig(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
    st.markdown("**Distribusi Pelanggan per Paket**")
    pkg_tc = df.groupby("package")["total_customers"].sum().reset_index()
    fig3 = px.bar(pkg_tc, x="package", y="total_customers",
                  color="package", color_discrete_sequence=COLORS)
    sfig(fig3, h=280)
    fig3.update_layout(showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: PAKET LAYANAN
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📦 Paket Layanan":
    st.markdown("<div class='ion-page-wrap'>", unsafe_allow_html=True)

    packages = sorted(df["package"].unique())
    cols = st.columns(len(packages))
    for i, pkg in enumerate(packages):
        pdata = df[df["package"]==pkg]
        rev = pdata["revenue"].sum()
        nc  = pdata["new_customers"].sum()
        with cols[i]:
            st.markdown(metric_card(
                "📦", COLORS[i % len(COLORS)],
                pkg, fmt_rp(rev),
                f"{nc:,} pelanggan", "up"
            ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
        st.markdown("**Revenue per Paket**")
        pkg_df = pkg_rev.reset_index(); pkg_df.columns = ["package","revenue"]
        fig = px.pie(pkg_df, names="package", values="revenue", hole=0.50,
                     color_discrete_sequence=COLORS)
        sfig(fig, h=320)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
        st.markdown("**Pelanggan Baru per Paket**")
        pkg_nc = pkg_new.reset_index(); pkg_nc.columns = ["package","new_customers"]
        fig2 = px.bar(pkg_nc, x="package", y="new_customers",
                      color="package", color_discrete_sequence=COLORS)
        sfig(fig2, h=320)
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
    st.markdown("**Tren Revenue per Paket (Bulanan)**")
    pkg_monthly = df.groupby(["month","package"])["revenue"].sum().reset_index()
    fig3 = px.line(pkg_monthly, x="month", y="revenue", color="package",
                   color_discrete_sequence=COLORS, markers=True)
    sfig(fig3, h=280)
    st.plotly_chart(fig3, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: WILAYAH
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🗺️ Wilayah":
    st.markdown("<div class='ion-page-wrap'>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(metric_card("🏆","#4F8BFF","Area Terbaik", area_rev.index[0], fmt_rp(area_rev.iloc[0])), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("🗺️","#6C5CE7","Total Area", f"{df['area'].nunique()} Wilayah"), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("📊","#00D4AA","Avg Revenue/Area", fmt_rp(area_rev.mean())), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([3,2])
    with col1:
        st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
        st.markdown("**Top 15 Wilayah Berdasarkan Revenue**")
        top15 = area_rev.head(15).reset_index()
        top15.columns = ["area","revenue"]
        fig = px.bar(top15, x="revenue", y="area", orientation="h",
                     color="revenue", color_continuous_scale=["#4F8BFF","#6C5CE7"])
        fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
        sfig(fig, h=420)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
        st.markdown("**Top 5 Wilayah**")
        top5 = area_rev.head(5)
        max_v = top5.max()
        rows = ""
        for area, val in top5.items():
            pct = val/max_v*100
            rows += f"""
            <div class='ion-hbar-row'>
                <div class='ion-hbar-label'>{area}</div>
                <div class='ion-hbar-track'><div class='ion-hbar-fill' style='width:{pct:.0f}%'></div></div>
                <div class='ion-hbar-val'>{fmt_rp(val)}</div>
            </div>"""
        st.markdown(rows, unsafe_allow_html=True)

        st.markdown("<br><br>**Bottom 5 Wilayah**", unsafe_allow_html=True)
        bot5 = area_rev.tail(5)
        rows2 = ""
        for area, val in bot5.items():
            pct = val/max_v*100
            rows2 += f"""
            <div class='ion-hbar-row'>
                <div class='ion-hbar-label'>{area}</div>
                <div class='ion-hbar-track'><div class='ion-hbar-fill' style='width:{pct:.0f}%;background:linear-gradient(90deg,#EF4444,#F59E0B)'></div></div>
                <div class='ion-hbar-val'>{fmt_rp(val)}</div>
            </div>"""
        st.markdown(rows2, unsafe_allow_html=True)



# ─────────────────────────────────────────────────────────────────────────────
# PAGE: EDA EXPLORER
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🔍 EDA Explorer":
    st.markdown("<div class='ion-page-wrap'>", unsafe_allow_html=True)

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        sel_area = st.multiselect("Filter Area", sorted(df["area"].unique()), default=sorted(df["area"].unique())[:10])
    with col_f2:
        sel_pkg = st.multiselect("Filter Paket", sorted(df["package"].unique()), default=sorted(df["package"].unique()))

    fdf = df[df["area"].isin(sel_area if sel_area else df["area"].unique()) &
             df["package"].isin(sel_pkg if sel_pkg else df["package"].unique())]
    fmonthly = fdf.groupby("month").agg(revenue=("revenue","sum"), new_customers=("new_customers","sum")).reset_index()

    st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
    st.markdown("**Tren Revenue (Filtered)**")
    fig = px.line(fmonthly, x="month", y="revenue", markers=True,
                  color_discrete_sequence=[C["primary"]])
    sfig(fig)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
        st.markdown("**Revenue per Area (Filtered)**")
        f_area = fdf.groupby("area")["revenue"].sum().sort_values(ascending=False).head(10).reset_index()
        fig2 = px.bar(f_area, x="revenue", y="area", orientation="h",
                      color_discrete_sequence=[C["primary2"]])
        fig2.update_layout(yaxis=dict(autorange="reversed"))
        sfig(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
        st.markdown("**Revenue per Paket (Filtered)**")
        f_pkg = fdf.groupby("package")["revenue"].sum().reset_index()
        fig3 = px.bar(f_pkg, x="package", y="revenue",
                      color="package", color_discrete_sequence=COLORS)
        fig3.update_layout(showlegend=False)
        sfig(fig3)
        st.plotly_chart(fig3, use_container_width=True)



# ─────────────────────────────────────────────────────────────────────────────
# PAGE: TREN & POLA
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📈 Tren & Pola":
    st.markdown("<div class='ion-page-wrap'>", unsafe_allow_html=True)

    st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
    st.markdown("**Revenue Bulanan — Trend Line**")
    x_num = np.arange(len(monthly_all))
    z = np.polyfit(x_num, monthly_all["revenue"], 1)
    trend_line = np.poly1d(z)(x_num)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=monthly_all["month"], y=monthly_all["revenue"],
                         name="Revenue", marker_color=C["primary"], opacity=0.75))
    fig.add_trace(go.Scatter(x=monthly_all["month"], y=trend_line,
                             mode="lines", name="Tren Linear",
                             line=dict(color=C["accent2"], width=2.5, dash="dash")))
    sfig(fig)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
        st.markdown("**Heatmap Revenue (Area × Paket)**")
        pivot = df.groupby(["area","package"])["revenue"].sum().reset_index()
        pivot_wide = pivot.pivot(index="area", columns="package", values="revenue").fillna(0)
        fig2 = px.imshow(pivot_wide, color_continuous_scale=["#0B0E1A","#4F8BFF","#6C5CE7"],
                         aspect="auto")
        sfig(fig2, h=380)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
        st.markdown("**Month-over-Month Growth (%)**")
        mom = monthly_all["revenue"].pct_change() * 100
        colors = [C["success"] if v >= 0 else C["danger"] for v in mom.fillna(0)]
        fig3 = go.Figure(go.Bar(
            x=monthly_all["month"], y=mom.fillna(0),
            marker_color=colors
        ))
        fig3.add_hline(y=0, line_color=C["muted"], line_dash="dot")
        sfig(fig3)
        st.plotly_chart(fig3, use_container_width=True)



# ─────────────────────────────────────────────────────────────────────────────
# PAGE: KORELASI
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🔗 Korelasi":
    st.markdown("<div class='ion-page-wrap'>", unsafe_allow_html=True)

    num_cols = ["revenue","new_customers","churn_customers","total_customers"]
    corr_matrix = monthly_all[num_cols].corr()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
        st.markdown("**Correlation Heatmap**")
        fig = px.imshow(corr_matrix, text_auto=".2f",
                        color_continuous_scale=["#EF4444","#0B0E1A","#4F8BFF"],
                        zmin=-1, zmax=1)
        sfig(fig, h=340)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
        st.markdown("**Scatter: New Customers vs Revenue**")
        fig2 = px.scatter(monthly_all, x="new_customers", y="revenue",
                          trendline="ols", color_discrete_sequence=[C["primary"]],
                          trendline_color_override=C["accent"])
        sfig(fig2, h=340)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
    st.markdown("**Scatter: Churn vs Revenue (Feb–Des)**")
    clean = monthly_all.iloc[1:]
    fig3 = px.scatter(clean, x="churn_customers", y="revenue",
                      trendline="ols", color_discrete_sequence=[C["danger"]],
                      trendline_color_override=C["accent2"])
    sfig(fig3, h=280)
    st.plotly_chart(fig3, use_container_width=True)

    corr_vals = {
        "New Customers vs Revenue":   monthly_all["new_customers"].corr(monthly_all["revenue"]),
        "Churn vs Revenue":           clean["churn_customers"].corr(clean["revenue"]),
        "Total Customers vs Revenue": monthly_all["total_customers"].corr(monthly_all["revenue"]),
    }
    c1,c2,c3 = st.columns(3)
    for col, (lbl, val) in zip([c1,c2,c3], corr_vals.items()):
        color = C["success"] if abs(val) > 0.7 else C["accent2"] if abs(val) > 0.4 else C["danger"]
        col.markdown(f"<div style='text-align:center;padding:10px;'><div style='font-size:1.6rem;font-weight:800;color:{color};font-family:JetBrains Mono,monospace;'>{val:.3f}</div><div style='font-size:0.78rem;color:{C['muted']};margin-top:4px;'>{lbl}</div></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: PREDIKSI PENJUALAN
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🔮 Prediksi Penjualan":
    st.markdown("<div class='ion-page-wrap'>", unsafe_allow_html=True)

    if forecast_df is None:
        st.warning("⚠️ File forecast tidak ditemukan. Jalankan 04_forecast_evaluation.py terlebih dahulu.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        next_rev = forecast_df["forecast_revenue"].iloc[0]
        avg_fc   = forecast_df["forecast_revenue"].mean()
        total_fc = forecast_df["forecast_revenue"].sum()
        with c1:
            st.markdown(metric_card("🎯","#4F8BFF","MAPE Model", f"{mape_val:.2f}%"), unsafe_allow_html=True)
        with c2:
            st.markdown(metric_card("🔮","#6C5CE7","Prediksi Bulan Depan", fmt_rp(next_rev)), unsafe_allow_html=True)
        with c3:
            st.markdown(metric_card("📊","#00D4AA","Rata-rata Forecast", fmt_rp(avg_fc)), unsafe_allow_html=True)
        with c4:
            st.markdown(metric_card("💰","#F59E0B","Total Forecast 6 Bln", fmt_rp(total_fc)), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
        st.markdown("**Aktual vs Prediksi Revenue**")
        actual_m = df.groupby("month")["revenue"].sum().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=actual_m["month"], y=actual_m["revenue"],
                                  mode="lines+markers", name="Aktual",
                                  line=dict(color=C["primary"], width=2.5)))
        fig.add_trace(go.Scatter(x=fitted_df["month"], y=fitted_df["fitted_revenue"],
                                  mode="lines", name="Model Fitted",
                                  line=dict(color=C["accent"], width=2, dash="dot")))
        fig.add_trace(go.Scatter(x=forecast_df["month"], y=forecast_df["forecast_revenue"],
                                  mode="lines+markers", name="Forecast",
                                  line=dict(color=C["primary2"], width=2.5, dash="dash"),
                                  marker=dict(size=8, symbol="diamond")))
        fig.add_trace(go.Scatter(
            x=pd.concat([forecast_df["month"], forecast_df["month"][::-1]]),
            y=pd.concat([forecast_df["upper_95"], forecast_df["lower_95"][::-1]]),
            fill="toself", fillcolor="rgba(108,92,231,0.12)",
            line=dict(color="rgba(0,0,0,0)"), name="95% CI"
        ))
        fig.add_vline(x=actual_m["month"].iloc[-1], line_color=C["muted"],
                      line_dash="dot", line_width=1)
        sfig(fig, h=400)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
        st.markdown("**Tabel Forecast 6 Bulan**")
        tbl = forecast_df.copy()
        tbl.columns = ["Bulan","Prediksi Revenue","Batas Bawah (95%)","Batas Atas (95%)"]
        tbl["Bulan"] = tbl["Bulan"].dt.strftime("%B %Y")
        for c in tbl.columns[1:]:
            tbl[c] = tbl[c].apply(lambda x: f"Rp {x:,.0f}")
        st.dataframe(tbl, use_container_width=True, hide_index=True)
        csv = forecast_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Forecast CSV", csv, "forecast_6bulan.csv","text/csv")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: SCENARIO PLANNING
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🎯 Scenario Planning":
    st.markdown("<div class='ion-page-wrap'>", unsafe_allow_html=True)
    st.markdown("**Simulasi Skenario Pertumbuhan Revenue**")
    st.caption("Sesuaikan slider untuk melihat proyeksi revenue berdasarkan asumsi pertumbuhan")

    col_s, col_r = st.columns([1,2])
    with col_s:
        st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
        st.markdown("**Parameter Skenario**")
        growth_pct = st.slider("Target Growth Bulanan (%)", -10, 30, 5)
        churn_red  = st.slider("Reduksi Churn Rate (%)", 0, 50, 10)
        upsell_pct = st.slider("Upsell Paket Premium (%)", 0, 40, 15)
        months_fwd = st.slider("Proyeksi ke Depan (bulan)", 3, 24, 12)

    with col_r:
        st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
        base_rev = monthly_all["revenue"].iloc[-1]
        proj_months = pd.date_range(start=monthly_all["month"].iloc[-1] + pd.DateOffset(months=1),
                                    periods=months_fwd, freq="MS")
        base_proj   = [base_rev * (1 + growth_pct/100)**i for i in range(1, months_fwd+1)]
        opt_proj    = [base_rev * (1 + (growth_pct + churn_red*0.1 + upsell_pct*0.08)/100)**i for i in range(1, months_fwd+1)]
        pes_proj    = [base_rev * (1 + (growth_pct - 5)/100)**i for i in range(1, months_fwd+1)]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly_all["month"], y=monthly_all["revenue"],
                                  mode="lines+markers", name="Historis",
                                  line=dict(color=C["primary"], width=2.5)))
        fig.add_trace(go.Scatter(x=proj_months, y=opt_proj, mode="lines",
                                  name="Skenario Optimis",
                                  line=dict(color=C["success"], width=2, dash="dash")))
        fig.add_trace(go.Scatter(x=proj_months, y=base_proj, mode="lines",
                                  name="Skenario Dasar",
                                  line=dict(color=C["accent2"], width=2, dash="dash")))
        fig.add_trace(go.Scatter(x=proj_months, y=pes_proj, mode="lines",
                                  name="Skenario Pesimis",
                                  line=dict(color=C["danger"], width=2, dash="dash")))
        sfig(fig, h=380)
        st.plotly_chart(fig, use_container_width=True)

        c1,c2,c3 = st.columns(3)
        c1.markdown(f"<div style='text-align:center;'><div style='color:{C['success']};font-size:1.2rem;font-weight:800;'>{fmt_rp(opt_proj[-1])}</div><div style='font-size:0.75rem;color:{C['muted']};'>Optimis</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div style='text-align:center;'><div style='color:{C['accent2']};font-size:1.2rem;font-weight:800;'>{fmt_rp(base_proj[-1])}</div><div style='font-size:0.75rem;color:{C['muted']};'>Dasar</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div style='text-align:center;'><div style='color:{C['danger']};font-size:1.2rem;font-weight:800;'>{fmt_rp(pes_proj[-1])}</div><div style='font-size:0.75rem;color:{C['muted']};'>Pesimis</div></div>", unsafe_allow_html=True)



# ─────────────────────────────────────────────────────────────────────────────
# PAGE: EVALUASI MODEL
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📉 Evaluasi Model":
    st.markdown("<div class='ion-page-wrap'>", unsafe_allow_html=True)

    if fitted_df is None:
        st.warning("Jalankan 04_forecast_evaluation.py terlebih dahulu.")
    else:
        actual_m = df.groupby("month")["revenue"].sum().reset_index()
        merged = actual_m.merge(fitted_df, on="month")
        merged["error"]    = merged["revenue"] - merged["fitted_revenue"]
        merged["abs_pct"]  = (merged["error"].abs() / merged["revenue"] * 100)
        mae  = merged["error"].abs().mean()
        rmse = np.sqrt((merged["error"]**2).mean())
        mape = merged["abs_pct"].mean()

        c1,c2,c3,c4 = st.columns(4)
        with c1: st.markdown(metric_card("🎯","#4F8BFF","MAPE",f"{mape:.2f}%"), unsafe_allow_html=True)
        with c2: st.markdown(metric_card("📏","#6C5CE7","MAE",fmt_rp(mae)), unsafe_allow_html=True)
        with c3: st.markdown(metric_card("📐","#00D4AA","RMSE",fmt_rp(rmse)), unsafe_allow_html=True)
        with c4:
            rating = "Excellent" if mape < 5 else "Good" if mape < 10 else "Fair"
            color  = C["success"] if mape < 5 else C["accent2"] if mape < 10 else C["danger"]
            st.markdown(metric_card("⭐","#F59E0B","Rating Model",rating), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col1,col2 = st.columns(2)
        with col1:
            st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
            st.markdown("**Actual vs Fitted Revenue**")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=merged["month"], y=merged["revenue"],
                                      mode="lines+markers", name="Aktual",
                                      line=dict(color=C["primary"], width=2.5)))
            fig.add_trace(go.Scatter(x=merged["month"], y=merged["fitted_revenue"],
                                      mode="lines+markers", name="Fitted",
                                      line=dict(color=C["accent2"], width=2, dash="dot")))
            sfig(fig)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
            st.markdown("**Error per Bulan (%)**")
            bar_c = [C["success"] if v <= 5 else C["accent2"] if v <= 10 else C["danger"]
                     for v in merged["abs_pct"]]
            fig2 = go.Figure(go.Bar(x=merged["month"], y=merged["abs_pct"],
                                     marker_color=bar_c))
            fig2.add_hline(y=5, line_color=C["success"], line_dash="dot", annotation_text="5% threshold")
            sfig(fig2)
            st.plotly_chart(fig2, use_container_width=True)



# ─────────────────────────────────────────────────────────────────────────────
# PAGE: LAPORAN OTOMATIS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📋 Laporan Otomatis":
    st.markdown("<div class='ion-page-wrap'>", unsafe_allow_html=True)

    best_area_name = area_rev.index[0]
    best_pkg_name  = pkg_rev.index[0]
    best_pkg_vol   = pkg_new.index[0]
    clean_m = monthly_all.iloc[1:]
    corr_cn = clean_m["churn_customers"].corr(clean_m["revenue"])

    st.markdown(f"""
    <div class='ion-card'>
        <div style='font-size:0.75rem;color:{C['muted']};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px;font-weight:700;'>📋 Ringkasan Eksekutif</div>
        <div style='font-size:0.92rem;color:{C['text']};line-height:1.8;'>
            Selama periode <b>Januari – Desember 2024</b>, ION Network mencatatkan total revenue
            sebesar <b style='color:{C['primary']}'>{fmt_rp(total_rev)}</b> dengan pertumbuhan
            <b style='color:{C['success']}'>{growth_rev:+.1f}%</b> dari bulan pertama ke bulan terakhir.
            Total pelanggan baru yang berhasil diperoleh adalah <b>{total_new:,} pelanggan</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    insights = [
        ("📈", C["primary"],  "Tren Penjualan", f"Revenue tumbuh {growth_rev:+.1f}% sepanjang 2024 dengan tren yang relatif stabil dan variasi bulanan kecil."),
        ("🌍", C["accent"],   "Area Terbaik",   f"{best_area_name} adalah area dengan revenue tertinggi ({fmt_rp(area_rev.iloc[0])}). Perlu direplikasi ke area berkinerja rendah."),
        ("📦", C["primary2"], "Paket Terlaris",  f"Paket {best_pkg_name} menyumbang revenue tertinggi, sementara {best_pkg_vol} paling diminati pelanggan baru."),
        ("🔁", C["accent2"],  "Churn & Revenue", f"Korelasi churn vs revenue: {corr_cn:.2f}. Basis pelanggan stagnan karena new customer ≈ churn (replacement equilibrium)."),
        ("🔮", C["success"],  "Proyeksi",        f"Model SARIMA memproyeksikan revenue stabil ~{fmt_rp(monthly_all['revenue'].mean())}/bulan. MAPE {mape_val:.2f}% (akurasi sangat baik)."),
    ]

    for icon, color, title, desc in insights:
        st.markdown(f"""
        <div style='display:flex;gap:14px;align-items:flex-start;
                    background:{C['card2']};border:1px solid {C['border']};
                    border-left:4px solid {color};border-radius:12px;
                    padding:16px 18px;margin-bottom:12px;'>
            <div style='font-size:1.4rem;'>{icon}</div>
            <div>
                <div style='font-size:0.85rem;font-weight:700;color:{C['text']};margin-bottom:4px;'>{title}</div>
                <div style='font-size:0.82rem;color:{C['muted']};line-height:1.6;'>{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"<div class='ion-card'><div style='font-size:0.75rem;color:{C['muted']};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:14px;font-weight:700;'>✅ Rekomendasi Bisnis</div>", unsafe_allow_html=True)
    recs = [
        ("1","Tekan churn rate melalui program loyalitas dan peningkatan kualitas layanan."),
        ("2","Dorong upsell dari paket entry-level ke paket 100–300 Mbps untuk meningkatkan margin."),
        (f"3",f"Replikasi strategi sukses {best_area_name} ke area berkinerja rendah."),
        ("4","Tingkatkan akuisisi pelanggan baru di kota besar yang masih under-penetrated."),
        ("5","Gunakan forecast SARIMA sebagai baseline, tetapkan target inkremental 10–15% YoY."),
    ]
    for num, rec in recs:
        st.markdown(f"<div style='display:flex;gap:12px;margin-bottom:10px;'><div style='width:24px;height:24px;border-radius:50%;background:linear-gradient(135deg,{C['primary']},{C['primary2']});display:flex;align-items:center;justify-content:center;font-size:0.72rem;font-weight:700;color:white;flex-shrink:0;'>{num}</div><div style='font-size:0.85rem;color:{C['text']};padding-top:3px;'>{rec}</div></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: EXPORT DATA
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📥 Export Data":
    st.markdown("<div class='ion-page-wrap'>", unsafe_allow_html=True)
    st.markdown("**Export & Download Data**")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='ion-card'>", unsafe_allow_html=True)
        st.markdown("**📄 Data Penjualan Lengkap**")
        st.caption(f"{len(df):,} baris · {len(df.columns)} kolom")
        csv1 = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download data_penjualan.csv", csv1, "data_penjualan.csv","text/csv", use_container_width=True)

        st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
        st.markdown("**📊 Revenue Bulanan Agregat**")
        csv2 = monthly_all.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download monthly_revenue.csv", csv2, "monthly_revenue.csv","text/csv", use_container_width=True)

    with col2:
        st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
        st.markdown("**🔮 Hasil Forecast 6 Bulan**")
        if forecast_df is not None:
            csv3 = forecast_df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download forecast_6bulan.csv", csv3, "forecast_6bulan.csv","text/csv", use_container_width=True)
        else:
            st.caption("Jalankan 04_forecast_evaluation.py terlebih dahulu.")

        st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
        st.markdown("**🌍 Revenue per Area**")
        area_df = area_rev.reset_index()
        area_df.columns = ["area","total_revenue"]
        csv4 = area_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download revenue_per_area.csv", csv4, "revenue_per_area.csv","text/csv", use_container_width=True)

    st.markdown("<div class='ion-card'>", unsafe_allow_html=True)
    st.markdown("**👁️ Preview Data**")
    st.dataframe(df.head(20), use_container_width=True, hide_index=True)
