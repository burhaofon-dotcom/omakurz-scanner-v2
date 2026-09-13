import math
from typing import Optional, Tuple

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np


# ============================================================
# OmaKurz™ Scanner v2.3 (Hotfix gegen NoneType-Fehler)
# ============================================================

st.set_page_config(
    page_title="OmaKurz™ Scanner v2.3",
    page_icon="🧓",
    layout="wide"
)

st.markdown(
    """
    <style>
    .main { padding-top: 1rem; }
    .stMetric { background-color: #1e2530; padding: 15px; border-radius: 10px; border: 1px solid #2d3748; }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HILFSFUNKTIONEN & SICHERE DATENBEREINIGUNG
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


def clean_series(series) -> pd.Series:
    """
    Absolut sichere Bereinigung, fängt None, DataFrames und leere Objekte ab.
    """
    if series is None:
        return pd.Series(dtype=float)
    if isinstance(series, pd.DataFrame):
        if series.empty:
            return pd.Series(dtype=float)
        series = series.iloc[:, 0]
    if not isinstance(series, pd.Series):
        try:
            series = pd.Series(series)
        except Exception:
            return pd.Series(dtype=float)
    try:
        result = pd.to_numeric(series, errors="coerce")
        result = result.dropna()
        result = result.sort_index()
        return result
    except Exception:
        return pd.Series(dtype=float)


def find_row(df: Optional[pd.DataFrame], candidates) -> pd.Series:
    """
    Sucht robust nach einer Finanzzeile und liefert IMMER eine Series (nie None).
    """
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return pd.Series(dtype=float)

    normalized = {
        str(idx).strip().lower(): idx
        for idx in df.index
    }

    # 1. Exakte Suche
    for candidate in candidates:
        key = candidate.strip().lower()
        if key in normalized:
            res = clean_series(df.loc[normalized[key]])
            if not res.empty:
                return res

    # 2. Teilstring-Suche
    for candidate in candidates:
        key = candidate.strip().lower()
        for normalized_key, original_key in normalized.items():
            if key in normalized_key:
                res = clean_series(df.loc[original_key])
                if not res.empty:
                    return res

    return pd.Series(dtype=float)


def percent_change(old, new) -> Optional[float]:
    old = safe_float(old)
    new = safe_float(new)
    if old is None or new is None or old == 0:
        return None
    return (new / old - 1.0) * 100.0


@st.cache_data(ttl=3600)
def get_global_fx_rate(currency: str) -> float:
    currency = (currency or "EUR").upper()
    if currency == "EUR":
        return 1.0
    if currency == "GBX":
        return 0.01 * get_global_fx_rate("GBP")
    
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
# ANALYSE-MODULE
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
    delta_changes = np.diff(deltas)

    if values[-1] < values[-2]:
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
        result["message"] = "Die Kennzahl wächst linear."
    return result


def calculate_margin_series(revenue_series: pd.Series, net_income_series: pd.Series) -> pd.Series:
    revenue = clean_series(revenue_series)
    net_income = clean_series(net_income_series)
    if revenue.empty or net_income.empty:
        return pd.Series(dtype=float)
    
    common_dates = revenue.index.intersection(net_income.index)
    if len(common_dates) == 0:
        return pd.Series(dtype=float)

    margins = {}
    for date in common_dates:
        rev = safe_float(revenue.loc[date])
        ni = safe_float(net_income.loc[date])
        if rev and ni and rev != 0:
            margins[date] = (ni / rev) * 100.0
    return pd.Series(margins).sort_index()


def classify_margin_trend(margin_series: pd.Series) -> dict:
    s = clean_series(margin_series)
    result = {"status": "Nicht ausreichend Daten", "score": 50, "message": "Keine Margen-Zeitreihe."}
    if len(s) < 2:
        return result
    
    change = safe_float(s.iloc[-1]) - safe_float(s.iloc[-2])
    if change > 2:
        result["status"] = "🟢 Margen verbessern sich"
        result["score"] = 85
        result["message"] = "Die Nettomarge ist zuletzt spürbar gestiegen."
    elif change < -2:
        result["status"] = "🟠 Margen verschlechtern sich"
        result["score"] = 35
        result["message"] = "Die Nettomarge ist zuletzt gefallen."
    else:
        result["status"] = "➡️ Margen stabil"
        result["score"] = 65
        result["message"] = "Die Nettomarge zeigt keine starke Veränderung."
    return result


def calculate_fcf(ocf_series: pd.Series, capex_series: pd.Series) -> pd.Series:
    ocf = clean_series(ocf_series)
    capex = clean_series(capex_series)
    if ocf.empty or capex_series.empty:
        return pd.Series(dtype=float)
    
    common_dates = ocf.index.intersection(capex_series.index)
    if len(common_dates) == 0:
        return pd.Series(dtype=float)

    fcf_values = {}
    for date in common_dates:
        o = safe_float(ocf.loc[date])
        c = safe_float(capex_series.loc[date])
        if o is not None and c is not None:
            fcf_values[date] = o + c 
    return pd.Series(fcf_values).sort_index()


def classify_fcf_dynamics(fcf_series: pd.Series) -> dict:
    s = clean_series(fcf_series)
    result = {"status": "Nicht ausreichend Daten", "score": 50, "message": "Keine FCF-Zeitreihe."}
    if len(s) < 2:
        return result
    
    latest, prev = safe_float(s.iloc[-1]), safe_float(s.iloc[-2])
    if latest is None or prev is None:
        return result

    if latest > 0 and prev > 0 and latest > prev:
        result["status"] = "🟢 FCF verbessert sich"
        result["score"] = 85
        result["message"] = "Der Free Cashflow ist positiv und gewachsen."
    elif latest > 0 and prev > 0 and latest < prev:
        result["status"] = "🟠 FCF schwächer"
        result["score"] = 50
        result["message"] = "Der FCF ist positiv, aber gesunken."
    elif latest < 0:
        result["status"] = "🔴 FCF negativ"
        result["score"] = 20
        result["message"] = "Der Free Cashflow ist negativ."
    else:
        result["status"] = "➡️ FCF uneinheitlich"
        result["score"] = 45
        result["message"] = "Kein klarer FCF-Trend."
    return result


def analyze_dilution(shares_series: pd.Series) -> dict:
    shares = clean_series(shares_series)
    result = {"status": "Nicht ausreichend Daten", "message": "Keine Aktienhistorie.", "share_change_pct": None}
    if len(shares) < 2:
        return result

    start, end = safe_float(shares.iloc[0]), safe_float(shares.iloc[-1])
    change = percent_change(start, end)
    result["share_change_pct"] = change

    if change is not None:
        if change > 5:
            result["status"] = "🔴 Aktienzahl deutlich gestiegen (Verwässerung)"
            result["message"] = "Die Anzahl der ausgegebenen Aktien ist gewachsen."
        elif change < -1:
            result["status"] = "🟢 Aktienzahl sinkt (Rückkäufe)"
            result["message"] = "Das Unternehmen reduziert aktiv die Aktienanzahl."
        else:
            result["status"] = "➡️ Aktienzahl stabil"
            result["message"] = "Keine nennenswerte Veränderung."
    return result


def calculate_evidence(revenue: pd.Series, ocf: pd.Series, capex: pd.Series, shares: pd.Series) -> dict:
    score = 0
    reasons, warnings = [], []

    if not clean_series(revenue).empty: score += 25; reasons.append("Umsatzdaten vorhanden")
    else: warnings.append("Keine Umsatzhistorie")

    if not clean_series(ocf).empty: score += 25; reasons.append("Cashflow vorhanden")
    else: warnings.append("Kein Cashflow")

    if not clean_series(shares).empty: score += 25; reasons.append("Aktienanzahl verfügbar")
    else: warnings.append("Aktienanzahl fehlt")

    if not clean_series(capex).empty: score += 25; reasons.append("CapEx verfügbar")
    else: warnings.append("CapEx fehlt")

    if score >= 75: level = "🟢 Gute Datengrundlage"
    elif score >= 50: level = "🟡 Brauchbar, aber Lücken"
    else: level = "🔴 Schwache Datengrundlage"

    return {"score": score, "level": level, "reasons": reasons, "warnings": warnings}


# ============================================================
# OBERFLÄCHE
# ============================================================

st.markdown("## 🧭 OMAKURZ™ Scanner v2.3")
col1, col2 = st.columns([2, 1])

with col1:
    ticker_input = st.text_input("Börsenkürzel eingeben:", "WKL.AS").upper().strip()
with col2:
    target_eur = st.number_input("Zielgröße (€)", min_value=100, max_value=50000, value=1000, step=100)

if st.button("⚡ OmaKurz v2.3 starten"):
    with st.spinner("Analysiere Finanzdaten..."):
        try:
            stock = yf.Ticker(ticker_input)
            info = stock.info if isinstance(stock.info, dict) else {}

            company_name = info.get("longName", ticker_input)
            sector = info.get("sector", "Unbekannt")
            currency = info.get("currency", "USD")
            raw_price = safe_float(info.get("currentPrice", info.get("regularMarketPrice")))

            fx_rate = get_global_fx_rate("GBP" if currency == "GBX" else currency)
            price_eur = (raw_price / 100.0 if currency == "GBX" else raw_price) * fx_rate if raw_price else None

            try: financials = stock.financials
            except Exception: financials = pd.DataFrame()

            try: balance_sheet = stock.balance_sheet
            except Exception: balance_sheet = pd.DataFrame()

            try: cashflow = stock.cashflow
            except Exception: cashflow = pd.DataFrame()

            revenue_series = find_row(financials, ["Total Revenue", "Operating Revenue"])
            net_income_series = find_row(financials, ["Net Income", "Net Income Common Stockholders"])
            shares_series = find_row(balance_sheet, ["Ordinary Shares Number", "Share Issued", "Common Stock"])
            ocf_series = find_row(cashflow, ["Operating Cash Flow", "Total Cash From Operating Activities"])
            capex_series = find_row(cashflow, ["Capital Expenditures", "Purchase Of Property, Plant, Equipment"])

            st.markdown(f"### 🏢 {company_name}")
            st.caption(f"Ticker: {ticker_input} | Sektor: {sector} | Währung: {currency}")

            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Aktueller Kurs", f"{price_eur:.2f} €" if price_eur else "N/A")
            with m2:
                latest_rev = safe_float(revenue_series.iloc[-1]) if not revenue_series.empty else None
                st.metric("Letzter Umsatz", f"{latest_rev:,.0f}" if latest_rev else "N/A")
            with m3:
                latest_shares = safe_float(shares_series.iloc[-1]) if not shares_series.empty else None
                st.metric("Aktienanzahl", f"{latest_shares:,.0f}" if latest_shares else "N/A")

            st.markdown("---")

            # Analysen ausführen
            accel = classify_acceleration(revenue_series)
            margin_series = calculate_margin_series(revenue_series, net_income_series)
            margin_trend = classify_margin_trend(margin_series)
            fcf_series = calculate_fcf(ocf_series, capex_series)
            fcf_dynamics = classify_fcf_dynamics(fcf_series)
            dilution = analyze_dilution(shares_series)
            evidence = calculate_evidence(revenue_series, ocf_series, capex_series, shares_series)

            # Darstellung der Module
            st.markdown(f"**Umsatz-Beschleunigung:** {accel['status']}")
            st.info(accel['message'])

            st.markdown(f"**Margen-Trend:** {margin_trend['status']}")
            st.write(margin_trend['message'])

            st.markdown(f"**Free Cashflow-Dynamik:** {fcf_dynamics['status']}")
            st.write(fcf_dynamics['message'])

            st.markdown(f"**Kapital & Aktienentwicklung:** {dilution['status']}")
            st.write(dilution['message'])

            st.markdown(f"**Evidenz-Grad:** {evidence['level']} ({evidence['score']}%)")

            if price_eur and price_eur > 0:
                shares_needed = target_eur / price_eur
                st.success(f"🎯 **Beate-Sandler-Ziel ({target_eur:,.0f} €):** Genau **{shares_needed:.1f} Aktien** benötigt (Aktueller Kurs: {price_eur:.2f} €).")
            else:
                st.warning("Kurs konnte für die Zielberechnung nicht ermittelt werden.")

            if not revenue_series.empty:
                st.markdown("#### 📈 Umsatzhistorie")
                st.line_chart(revenue_series)

        except Exception as e:
            st.error(f"Fehler bei der Ausführung: {e}")

# ============================================================
# GLOSSAR
# ============================================================
with st.expander("📖 OmaKurz™ Glossar & Erklärungen"):
    st.markdown("""
    * **Umsatz-Beschleunigung:** Prüft, ob die Zuwächse von Jahr zu Jahr größer werden.
    * **Margen-Trend:** Überwacht die Entwicklung der Nettomarge.
    * **FCF-Dynamik:** Analysiert die Entwicklung des Free Cashflows (Operativer Cashflow minus Investitionen).
    * **Kapital- & Aktienentwicklung:** Zeigt Verwässerung oder Aktienrückkäufe an.
    * **Evidenz-Grad:** Bewertet die Datenvollständigkeit aus den Finanzberichten.
    """)
