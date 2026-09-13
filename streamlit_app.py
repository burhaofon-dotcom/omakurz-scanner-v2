
import math
from typing import Optional, Tuple

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np


# ============================================================
# OmaKurz™ Scanner v2.3
# ============================================================
# Grundprinzip:
#
#   🏛️ OMA       = Substanz
#   🚀 KURZ       = Zukunft
#   ⚡ DYNAMIK    = Beschleunigung / Verlangsamung
#   💰 FINANZ     = Kapitalbedarf / Finanzierung
#   🧬 PIPELINE   = Entwicklung / Zukunftsprogramme
#   🔍 EVIDENZ    = Datenqualität / Belegstärke
#   💎 QUALITÄT   = Qualitätsklasse
#
# Wichtig:
# - Kein Buy/Hold/Sell
# - Keine Kursziel-Magie
# - Keine automatische Kaufempfehlung
# - Qualität != Bewertung
# - Datenlücken werden sichtbar gemacht
# - Aussagen werden nicht stärker formuliert als die Datenlage
# ============================================================


st.set_page_config(
    page_title="OmaKurz™ Scanner v2.3",
    page_icon="🧓",
    layout="wide"
)


# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>
    .main {
        padding-top: 1rem;
    }

    .omakurz-card {
        padding: 1rem 1.2rem;
        border-radius: 14px;
        border: 1px solid rgba(128,128,128,0.25);
        margin-bottom: 1rem;
    }

    .small-muted {
        color: #777;
        font-size: 0.85rem;
    }

    .big-score {
        font-size: 2.2rem;
        font-weight: 700;
    }

    .warning-box {
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(200,120,0,0.35);
        background: rgba(255,180,0,0.08);
    }

    .danger-box {
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(200,0,0,0.35);
        background: rgba(255,0,0,0.06);
    }

    .success-box {
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(0,140,70,0.35);
        background: rgba(0,180,80,0.06);
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HILFSFUNKTIONEN
# ============================================================

def safe_float(value) -> Optional[float]:
    try:
        if value is None:
            return None
        if isinstance(value, (pd.Series, pd.DataFrame)):
            if value.empty:
                return None
            value = value.iloc[0]
        value = float(value)
        if not np.isfinite(value):
            return None
        return value
    except Exception:
        return None


def clean_series(series: Optional[pd.Series]) -> pd.Series:
    if series is None:
        return pd.Series(dtype=float)
    try:
        result = pd.to_numeric(series, errors="coerce")
        result = result.dropna()
        result = result.sort_index()
        return result
    except Exception:
        return pd.Series(dtype=float)


def find_row(df: Optional[pd.DataFrame], candidates) -> Optional[pd.Series]:
    if df is None or df.empty:
        return None
    normalized = {
        str(idx).strip().lower(): idx
        for idx in df.index
    }
    for candidate in candidates:
        key = candidate.strip().lower()
        if key in normalized:
            return clean_series(df.loc[normalized[key]])
    for candidate in candidates:
        key = candidate.strip().lower()
        for normalized_key, original_key in normalized.items():
            if key in normalized_key:
                return clean_series(df.loc[original_key])
    return None


def latest_value(series: Optional[pd.Series]) -> Optional[float]:
    s = clean_series(series)
    if s.empty:
        return None
    return safe_float(s.iloc[-1])


def first_value(series: Optional[pd.Series]) -> Optional[float]:
    s = clean_series(series)
    if s.empty:
        return None
    return safe_float(s.iloc[0])


def percent_change(old, new) -> Optional[float]:
    old = safe_float(old)
    new = safe_float(new)
    if old is None or new is None or old == 0:
        return None
    return (new / old - 1.0) * 100.0


def format_eur(value: Optional[float]) -> str:
    if value is None:
        return "n/a"
    abs_value = abs(value)
    if abs_value >= 1_000_000_000:
        return f"{value / 1_000_000_000:,.2f} Mrd. €"
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:,.2f} Mio. €"
    if abs_value >= 1_000:
        return f"{value / 1_000:,.1f} Tsd. €"
    return f"{value:,.2f} €"


def format_number(value: Optional[float]) -> str:
    if value is None:
        return "n/a"
    return f"{value:,.0f}".replace(",", ".")


def format_percent(value: Optional[float]) -> str:
    if value is None:
        return "n/a"
    return f"{value:+.1f} %"


# ============================================================
# FX
# ============================================================

@st.cache_data(ttl=3600)
def get_global_fx_rate(currency: str) -> float:
    currency = (currency or "EUR").upper()
    if currency == "EUR":
        return 1.0
    if currency == "GBX":
        gbp_rate = get_global_fx_rate("GBP")
        return 0.01 * gbp_rate
    
    fallback = {
        "USD": 0.92, "GBP": 1.17, "JPY": 0.0061, "HKD": 0.118,
        "SGD": 0.69, "CHF": 1.07, "CAD": 0.68, "AUD": 0.61,
    }
    try:
        ticker = yf.Ticker(f"{currency}EUR=X")
        quote = ticker.history(period="5d")
        if not quote.empty:
            value = safe_float(quote["Close"].dropna().iloc[-1])
            if value is not None and value > 0:
                return value
    except Exception:
        pass
    return fallback.get(currency, 1.0)


# ============================================================
# BESCHLEUNIGUNG & ANALYSEN
# ============================================================

def classify_acceleration(series: pd.Series) -> dict:
    s = clean_series(series)
    result = {
        "status": "Nicht ausreichend Daten", "score": 0,
        "deltas": [], "delta_changes": [], "growth_rates": [],
        "message": "Für eine belastbare Beschleunigungsanalyse fehlen historische Daten."
    }
    if len(s) < 3:
        return result

    values = s.values.astype(float)
    deltas = np.diff(values)
    growth_rates = []
    for old, new in zip(values[:-1], values[1:]):
        if old != 0:
            growth_rates.append((new / old - 1.0) * 100.0)
        else:
            growth_rates.append(np.nan)

    delta_changes = np.diff(deltas)
    latest_value_ = values[-1]

    if latest_value_ < values[-2]:
        result["status"] = "🔴 Rückläufig"
        result["score"] = 20
        result["message"] = "Die jüngste Kennzahl liegt unter dem Vorjahreswert."
    elif len(delta_changes) >= 1 and delta_changes[-1] > 0:
        result["status"] = "🟢 Beschleunigend"
        result["score"] = 90
        result["message"] = "Die absoluten Zuwächse werden größer."
    elif len(delta_changes) >= 1 and delta_changes[-1] < 0:
        result["status"] = "🟠 Verlangsamend"
        result["score"] = 50
        result["message"] = "Die Kennzahl wächst, aber der zusätzliche Zuwachs wird kleiner."
    else:
        result["status"] = "➡️ Wachsend, nicht beschleunigend"
        result["score"] = 65
        result["message"] = "Die Kennzahl wächst linear ohne zusätzliche Beschleunigung."

    result["deltas"] = deltas.tolist()
    result["delta_changes"] = delta_changes.tolist()
    result["growth_rates"] = growth_rates
    return result


def analyze_dilution(shares_series: pd.Series, revenue_series: pd.Series, fcf_series: pd.Series) -> dict:
    shares = clean_series(shares_series)
    revenue = clean_series(revenue_series)
    fcf = clean_series(fcf_series)

    result = {
        "status": "Nicht ausreichend Daten",
        "message": "Keine belastbare Aktienzahlhistorie.",
        "share_change_pct": None, "revenue_change_pct": None,
        "fcf_change_pct": None, "share_start": None, "share_end": None
    }

    if len(shares) < 2:
        return result

    share_start = safe_float(shares.iloc[0])
    share_end = safe_float(shares.iloc[-1])
    share_change = percent_change(share_start, share_end)

    result["share_start"] = share_start
    result["share_end"] = share_end
    result["share_change_pct"] = share_change

    if len(revenue) >= 2:
        result["revenue_change_pct"] = percent_change(revenue.iloc[0], revenue.iloc[-1])

    if share_change is not None:
        if share_change > 5:
            result["status"] = "🔴 Aktienzahl deutlich gestiegen (Verwässerungsdruck)"
            result["message"] = "Die Anzahl der ausgegebenen Aktien ist über den Zeitraum spürbar gewachsen."
        elif share_change < -1:
            result["status"] = "🟢 Aktienzahl sinkt (Aktienrückkäufe)"
            result["message"] = "Das Unternehmen reduziert aktiv die Aktienanzahl."
        else:
            result["status"] = "➡️ Aktienzahl weitgehend stabil"
            result["message"] = "Keine nennenswerte Veränderung der Aktienanzahl."
    return result


# ============================================================
# HAUPT-BENUTZEROBERFLÄCHE
# ============================================================

st.markdown("## 🧭 OMAKURZ™ Scanner v2.3")
col1, col2 = st.columns([2, 1])

with col1:
    ticker_input = st.text_input("Börsenkürzel eingeben (z.B. 7203.T, WKL.AS, FDS):", "WKL.AS").upper().strip()
with col2:
    target_eur = st.number_input("Zielgröße (€)", min_value=100, max_value=50000, value=1000, step=100)

if st.button("⚡ OmaKurz v2.3 starten"):
    try:
        stock = yf.Ticker(ticker_input)
        info = stock.info

        company_name = info.get("longName", ticker_input)
        sector = info.get("sector", "Unbekannt")
        currency = info.get("currency", "USD")
        raw_price = safe_float(info.get("currentPrice", info.get("regularMarketPrice")))

        fx_rate = get_global_fx_rate("GBP" if currency == "GBX" else currency)
        price_eur = (raw_price / 100.0 if currency == "GBX" else raw_price) * fx_rate if raw_price else None

        try: financials = stock.financials
        except Exception: financials = pd.DataFrame()

        try: cashflow = stock.cashflow
        except Exception: cashflow = pd.DataFrame()

        try: balance_sheet = stock.balance_sheet
        except Exception: balance_sheet = pd.DataFrame()

        rev_row = find_row(financials, ["Total Revenue", "Operating Revenue"])
        shares_row = find_row(balance_sheet, ["Ordinary Shares Number", "Share Issued"])

        revenue_series = clean_series(financials.loc[rev_row] if rev_row is not None else None)
        shares_series = clean_series(balance_sheet.loc[shares_row] if shares_row is not None else None)

        st.markdown(f"### 🏢 {company_name}")
        st.caption(f"Ticker: {ticker_input} | Sektor: {sector} | Währung: {currency}")

        # Beschleunigung ausgeben
        accel = classify_acceleration(revenue_series)
        st.markdown(f"**Umsatz-Beschleunigung:** {accel['status']}")
        st.info(accel['message'])

        # Dilution ausgeben
        dilution = analyze_dilution(shares_series, revenue_series, pd.Series(dtype=float))
        st.markdown(f"**Kapital- & Aktienentwicklung:** {dilution['status']}")
        st.write(dilution['message'])

        # Beate-Sandler-Ziel
        if price_eur and price_eur > 0:
            shares_needed = target_eur / price_eur
            st.success(f"🎯 **Beate-Sandler-Ziel ({target_eur:,.0f} €):** Genau **{shares_needed:.1f} Aktien** benötigt (Aktueller Kurs: {price_eur:.2f} €).")
        else:
            st.warning("Kurs konnte für die Zielberechnung nicht ermittelt werden.")

    except Exception as e:
        st.error(f"Fehler bei der Ausführung: {e}")
        
