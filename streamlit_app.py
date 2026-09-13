
import math
from typing import Optional, List, Dict, Any

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np


# ============================================================
# OmaKurz™ Scanner v2.4
# ============================================================
#
# 🏛️ OMA        = Substanz
# 🚀 KURZ       = Zukunft
# ⚡ DYNAMIK    = Wachstum und Beschleunigung
# 💰 KAPITAL    = Finanzierung und Aktienentwicklung
# 🕵️ DETEKTIV   = Cash, Debt und Runway
# 🔍 EVIDENZ    = Datenqualität und Datenlücken
# 🧬 PIPELINE   = Zukunftsprogramme
# 🧠 REALITY    = Story versus belegbare Daten
# ⚖️ BEWERTUNG  = Erwartung und Sicherheitsmarge
# 💎 QUALITÄT   = Rohstein bis Kronjuwel
# 🔨 OMA-HAMMER = harte Warnsignale
#
# WICHTIG:
# - Kein Buy / Hold / Sell
# - Keine automatische Kaufempfehlung
# - Kein künstliches Kursziel
# - Qualität ist nicht dasselbe wie Bewertung
# - Aktienanstieg ist nicht automatisch bewiesene Verwässerung
# - yfinance ist keine automatische Primärquellenprüfung
# - Pipeline-Daten werden nicht erfunden
# ============================================================


# ============================================================
# SEITENKONFIGURATION
# ============================================================

st.set_page_config(
    page_title="OmaKurz™ Scanner v2.4",
    page_icon="🧓",
    layout="wide",
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

    .omakurz-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }

    .omakurz-subtitle {
        color: #888;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }

    .quality-card {
        padding: 1.4rem;
        border-radius: 16px;
        border: 1px solid rgba(128,128,128,0.30);
        margin: 1rem 0;
    }

    .quality-title {
        font-size: 2rem;
        font-weight: 800;
    }

    .quality-description {
        font-size: 1.02rem;
        line-height: 1.65;
    }

    .oma-quote {
        padding: 1rem;
        border-left: 4px solid #888;
        margin: 1rem 0;
        font-style: italic;
        line-height: 1.6;
    }

    .warning-box {
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(220,150,0,0.35);
        background: rgba(255,180,0,0.08);
        margin-bottom: 0.8rem;
    }

    .danger-box {
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(220,0,0,0.35);
        background: rgba(255,0,0,0.06);
        margin-bottom: 0.8rem;
    }

    .success-box {
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(0,160,80,0.35);
        background: rgba(0,180,80,0.06);
        margin-bottom: 0.8rem;
    }

    .neutral-box {
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.25);
        background: rgba(128,128,128,0.05);
        margin-bottom: 0.8rem;
    }

    .glossary-term {
        font-weight: 700;
        font-size: 1.05rem;
    }

    .small-note {
        color: #888;
        font-size: 0.85rem;
        line-height: 1.5;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# ALLGEMEINE HILFSFUNKTIONEN
# ============================================================

def safe_float(value) -> Optional[float]:
    """Konvertiert einen Wert robust in eine endliche Zahl."""

    try:
        if value is None:
            return None

        if isinstance(value, pd.DataFrame):
            if value.empty:
                return None
            value = value.iloc[0, 0]

        elif isinstance(value, pd.Series):
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
    """Liefert immer eine bereinigte numerische Series."""

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

        try:
            result = result.sort_index()
        except Exception:
            pass

        return result.astype(float)

    except Exception:
        return pd.Series(dtype=float)


def normalize_dataframe(df) -> pd.DataFrame:
    """Normalisiert DataFrames möglichst robust."""

    if df is None:
        return pd.DataFrame()

    if not isinstance(df, pd.DataFrame):
        return pd.DataFrame()

    if df.empty:
        return pd.DataFrame()

    result = df.copy()

    if isinstance(result.index, pd.MultiIndex):
        try:
            result.index = result.index.get_level_values(-1)
        except Exception:
            pass

    return result


def find_row(
    df: Optional[pd.DataFrame],
    candidates: List[str],
) -> pd.Series:
    """
    Sucht eine Finanzzeile.

    Es wird zuerst exakt und danach vorsichtig per Teilstring gesucht.
    """

    df = normalize_dataframe(df)

    if df.empty:
        return pd.Series(dtype=float)

    normalized = {
        str(index).strip().lower(): index
        for index in df.index
    }

    for candidate in candidates:
        key = str(candidate).strip().lower()

        if key in normalized:
            result = clean_series(
                df.loc[normalized[key]]
            )

            if not result.empty:
                return result

    for candidate in candidates:
        key = str(candidate).strip().lower()

        for normalized_key, original_key in normalized.items():
            if key in normalized_key:
                result = clean_series(
                    df.loc[original_key]
                )

                if not result.empty:
                    return result

    return pd.Series(dtype=float)


def find_share_row(
    balance_sheet: Optional[pd.DataFrame],
    financials: Optional[pd.DataFrame],
) -> pd.Series:
    """
    Sucht nach echten Aktienzahl-Kennzahlen.

    Wichtig:
    'Common Stock' wird bewusst NICHT verwendet, weil es häufig
    einen Bilanzwert und nicht die Anzahl der Aktien beschreibt.
    """

    balance_sheet = normalize_dataframe(balance_sheet)
    financials = normalize_dataframe(financials)

    share_candidates = [
        "Ordinary Shares Number",
        "Share Issued",
        "Shares Issued",
        "Common Stock Shares Outstanding",
    ]

    result = find_row(
        balance_sheet,
        share_candidates,
    )

    if not result.empty:
        return result

    result = find_row(
        financials,
        share_candidates,
    )

    return result


def latest_value(series) -> Optional[float]:
    s = clean_series(series)

    if s.empty:
        return None

    return safe_float(s.iloc[-1])


def first_value(series) -> Optional[float]:
    s = clean_series(series)

    if s.empty:
        return None

    return safe_float(s.iloc[0])


def percent_change(
    old,
    new,
) -> Optional[float]:

    old = safe_float(old)
    new = safe_float(new)

    if old is None or new is None:
        return None

    if old == 0:
        return None

    return ((new / old) - 1.0) * 100.0


def format_number(
    value: Optional[float],
) -> str:

    if value is None:
        return "n/a"

    return f"{value:,.0f}".replace(",", ".")


def format_percent(
    value: Optional[float],
) -> str:

    if value is None:
        return "n/a"

    return f"{value:+.1f} %"


def format_eur(
    value: Optional[float],
) -> str:

    if value is None:
        return "n/a"

    absolute = abs(value)

    if absolute >= 1_000_000_000:
        return f"{value / 1_000_000_000:,.2f} Mrd. €"

    if absolute >= 1_000_000:
        return f"{value / 1_000_000:,.2f} Mio. €"

    if absolute >= 1_000:
        return f"{value / 1_000:,.1f} Tsd. €"

    return f"{value:,.2f} €"


def format_native(
    value: Optional[float],
    currency: str,
) -> str:

    if value is None:
        return "n/a"

    currency = currency or ""

    absolute = abs(value)

    if absolute >= 1_000_000_000:
        return f"{value / 1_000_000_000:,.2f} Mrd. {currency}"

    if absolute >= 1_000_000:
        return f"{value / 1_000_000:,.2f} Mio. {currency}"

    if absolute >= 1_000:
        return f"{value / 1_000:,.1f} Tsd. {currency}"

    return f"{value:,.2f} {currency}"


# ============================================================
# FX
# ============================================================

@st.cache_data(ttl=3600)
def get_global_fx_rate(currency: str) -> float:

    currency = (currency or "EUR").upper()

    if currency == "EUR":
        return 1.0

    if currency == "GBX":
        return 0.01 * get_global_fx_rate("GBP")

    fallback = {
        "USD": 0.92,
        "GBP": 1.17,
        "JPY": 0.0061,
        "HKD": 0.118,
        "SGD": 0.69,
        "CHF": 1.07,
        "CAD": 0.68,
        "AUD": 0.61,
    }

    try:
        fx_ticker = yf.Ticker(
            f"{currency}EUR=X"
        )

        history = fx_ticker.history(
            period="5d"
        )

        if not history.empty:
            close = history["Close"].dropna()

            if not close.empty:
                value = safe_float(close.iloc[-1])

                if value is not None and value > 0:
                    return value

    except Exception:
        pass

    return fallback.get(currency, 1.0)


# ============================================================
# BESCHLEUNIGUNG
# ============================================================

def classify_acceleration(
    series: pd.Series,
) -> dict:

    s = clean_series(series)

    result = {
        "status": "Nicht ausreichend Daten",
        "score": 0,
        "deltas": [],
        "delta_changes": [],
        "growth_rates": [],
        "message": (
            "Für eine belastbare Beschleunigungsanalyse "
            "fehlen historische Daten."
        ),
    }

    if len(s) < 3:
        return result

    values = s.values.astype(float)

    deltas = np.diff(values)
    delta_changes = np.diff(deltas)

    growth_rates = []

    for old, new in zip(values[:-1], values[1:]):
        if old != 0:
            growth_rates.append(
                (new / old - 1.0) * 100.0
            )
        else:
            growth_rates.append(np.nan)

    result["deltas"] = deltas.tolist()
    result["delta_changes"] = delta_changes.tolist()
    result["growth_rates"] = growth_rates

    if values[-1] < values[-2]:

        result["status"] = "🔴 Rückläufig"
        result["score"] = 20
        result["message"] = (
            "Die jüngste Kennzahl liegt unter dem "
            "vorherigen Vergleichswert. Das ist kein "
            "Beschleunigungssignal, sondern zunächst "
            "ein Rückgang."
        )

        return result

    if delta_changes[-1] > 0:

        result["status"] = "🟢 Beschleunigend"
        result["score"] = 90
        result["message"] = (
            "Die absoluten Zuwächse werden größer. "
            "Das spricht für eine echte operative "
            "Beschleunigung und nicht lediglich für "
            "weiteres Wachstum."
        )

        return result

    if delta_changes[-1] < 0:

        result["status"] = "🟠 Verlangsamend"
        result["score"] = 50
        result["message"] = (
            "Die Kennzahl wächst noch, aber der "
            "zusätzliche Zuwachs wird kleiner. "
            "Wachstum und Beschleunigung sind hier "
            "also nicht dasselbe."
        )

        return result

    result["status"] = "➡️ Wachsend, nicht beschleunigend"
    result["score"] = 65
    result["message"] = (
        "Die Kennzahl wächst, zeigt aber keine "
        "klare zusätzliche Beschleunigung."
    )

    return result


# ============================================================
# MARGEN
# ============================================================

def calculate_margin_series(
    revenue_series: pd.Series,
    net_income_series: pd.Series,
) -> pd.Series:

    revenue = clean_series(revenue_series)
    net_income = clean_series(net_income_series)

    if revenue.empty or net_income.empty:
        return pd.Series(dtype=float)

    common_dates = revenue.index.intersection(
        net_income.index
    )

    if len(common_dates) == 0:
        return pd.Series(dtype=float)

    margins = {}

    for date in common_dates:

        rev = safe_float(revenue.loc[date])
        ni = safe_float(net_income.loc[date])

        if (
            rev is not None
            and ni is not None
            and rev != 0
        ):
            margins[date] = (ni / rev) * 100.0

    return pd.Series(margins).sort_index()


def classify_margin_trend(
    margin_series: pd.Series,
) -> dict:

    s = clean_series(margin_series)

    result = {
        "status": "Nicht ausreichend Daten",
        "score": 50,
        "message": (
            "Keine ausreichende Margen-Zeitreihe."
        ),
    }

    if len(s) < 2:
        return result

    latest = safe_float(s.iloc[-1])
    previous = safe_float(s.iloc[-2])

    if latest is None or previous is None:
        return result

    change = latest - previous

    if change > 2:

        result["status"] = "🟢 Margen verbessern sich"
        result["score"] = 85
        result["message"] = (
            "Die Nettomarge ist zuletzt spürbar "
            "gestiegen. Das kann darauf hindeuten, "
            "dass zusätzliches Geschäft zunehmend "
            "profitabler wird."
        )

    elif change < -2:

        result["status"] = "🟠 Margen verschlechtern sich"
        result["score"] = 35
        result["message"] = (
            "Die Nettomarge ist zuletzt spürbar "
            "gefallen. Hier sollte geprüft werden, "
            "ob es sich um einen vorübergehenden "
            "Effekt oder eine strukturelle Verschlechterung handelt."
        )

    else:

        result["status"] = "➡️ Margen stabil"
        result["score"] = 65
        result["message"] = (
            "Die Nettomarge zeigt zuletzt keine "
            "starke Veränderung."
        )

    return result


# ============================================================
# FREE CASHFLOW
# ============================================================

def calculate_fcf(
    ocf_series: pd.Series,
    capex_series: pd.Series,
) -> pd.Series:

    ocf = clean_series(ocf_series)
    capex = clean_series(capex_series)

    if ocf.empty or capex.empty:
        return pd.Series(dtype=float)

    common_dates = ocf.index.intersection(
        capex.index
    )

    if len(common_dates) == 0:
        return pd.Series(dtype=float)

    values = {}

    for date in common_dates:

        operating_cf = safe_float(
            ocf.loc[date]
        )

        capital_expenditure = safe_float(
            capex.loc[date]
        )

        if (
            operating_cf is not None
            and capital_expenditure is not None
        ):
            values[date] = (
                operating_cf
                + capital_expenditure
            )

    return pd.Series(values).sort_index()


def classify_fcf_dynamics(
    fcf_series: pd.Series,
) -> dict:

    s = clean_series(fcf_series)

    result = {
        "status": "Nicht ausreichend Daten",
        "score": 50,
        "message": (
            "Keine ausreichende FCF-Zeitreihe."
        ),
    }

    if len(s) < 2:
        return result

    latest = safe_float(s.iloc[-1])
    previous = safe_float(s.iloc[-2])

    if latest is None or previous is None:
        return result

    if latest > 0 and previous <= 0:

        result["status"] = "🟢 FCF dreht positiv"
        result["score"] = 90
        result["message"] = (
            "Der Free Cashflow ist zuletzt in den "
            "positiven Bereich gedreht."
        )

    elif latest > 0 and previous > 0 and latest > previous:

        result["status"] = "🟢 FCF verbessert sich"
        result["score"] = 85
        result["message"] = (
            "Der positive Free Cashflow hat sich "
            "gegenüber dem vorherigen Zeitraum verbessert."
        )

    elif latest > 0 and previous > 0 and latest < previous:

        result["status"] = "🟠 FCF schwächer"
        result["score"] = 50
        result["message"] = (
            "Der Free Cashflow bleibt positiv, ist "
            "aber gegenüber dem vorherigen Zeitraum gefallen."
        )

    elif latest < 0 and previous < 0 and latest < previous:

        result["status"] = "🔴 FCF-Belastung steigt"
        result["score"] = 20
        result["message"] = (
            "Der negative Free Cashflow ist zuletzt "
            "noch negativer geworden."
        )

    elif latest < 0:

        result["status"] = "🟠 FCF negativ"
        result["score"] = 30
        result["message"] = (
            "Der Free Cashflow ist aktuell negativ. "
            "Damit ist besonders wichtig, wie viel "
            "Liquidität vorhanden ist und wie lange "
            "diese den Mittelabfluss tragen kann."
        )

    else:

        result["status"] = "➡️ FCF uneinheitlich"
        result["score"] = 45
        result["message"] = (
            "Die FCF-Entwicklung ist aktuell nicht eindeutig."
        )

    return result


# ============================================================
# AKTIENENTWICKLUNG
# ============================================================

def analyze_dilution(
    shares_series: pd.Series,
    revenue_series: pd.Series,
    fcf_series: pd.Series,
) -> dict:

    shares = clean_series(shares_series)
    revenue = clean_series(revenue_series)
    fcf = clean_series(fcf_series)

    result = {
        "status": "Nicht ausreichend Daten",
        "message": (
            "Keine belastbare Aktienhistorie."
        ),
        "share_change_pct": None,
        "revenue_change_pct": None,
        "fcf_change_pct": None,
        "share_start": None,
        "share_end": None,
    }

    if len(shares) < 2:
        return result

    start = safe_float(shares.iloc[0])
    end = safe_float(shares.iloc[-1])

    change = percent_change(start, end)

    result["share_start"] = start
    result["share_end"] = end
    result["share_change_pct"] = change

    if len(revenue) >= 2:
        result["revenue_change_pct"] = percent_change(
            revenue.iloc[0],
            revenue.iloc[-1],
        )

    if len(fcf) >= 2:

        old_fcf = safe_float(fcf.iloc[0])
        new_fcf = safe_float(fcf.iloc[-1])

        if (
            old_fcf is not None
            and new_fcf is not None
            and old_fcf > 0
        ):
            result["fcf_change_pct"] = percent_change(
                old_fcf,
                new_fcf,
            )

    if change is None:
        return result

    if change <= 3:

        result["status"] = "🟢 Aktienzahl weitgehend stabil"
        result["message"] = (
            "Die Aktienzahl hat sich über den "
            "betrachteten Zeitraum nur gering verändert. "
            "Das ist ein positives Signal für die Stabilität "
            "der bestehenden Beteiligungsbasis."
        )

        return result

    if change <= 10:

        result["status"] = "🟡 Aktienzahl gestiegen"
        result["message"] = (
            "Die Aktienzahl ist gestiegen. Das kann "
            "verschiedene Ursachen haben, beispiels
