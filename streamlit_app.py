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
    """
    Konvertiert Werte möglichst robust in float.
    Gibt None zurück, wenn keine sinnvolle Zahl vorliegt.
    """
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
    """
    Bereinigt eine historische Zeitreihe:
    - numerisch
    - NaN entfernt
    - nach Datum sortiert
    """
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
    """
    Sucht robust nach einer Finanzzeile.
    Die Suche erfolgt sowohl exakt als auch über Teilstrings.
    """
    if df is None or df.empty:
        return None

    normalized = {
        str(idx).strip().lower(): idx
        for idx in df.index
    }

    # 1. Exakte Suche
    for candidate in candidates:
        key = candidate.strip().lower()

        if key in normalized:
            return clean_series(df.loc[normalized[key]])

    # 2. Teilstring-Suche
    for candidate in candidates:
        key = candidate.strip().lower()

        for normalized_key, original_key in normalized.items():
            if key in normalized_key:
                return clean_series(df.loc[original_key])

    return None


def latest_value(series: Optional[pd.Series]) -> Optional[float]:
    """
    Gibt den jüngsten Wert einer Zeitreihe zurück.
    """
    s = clean_series(series)

    if s.empty:
        return None

    return safe_float(s.iloc[-1])


def first_value(series: Optional[pd.Series]) -> Optional[float]:
    """
    Gibt den ältesten Wert einer Zeitreihe zurück.
    """
    s = clean_series(series)

    if s.empty:
        return None

    return safe_float(s.iloc[0])


def percent_change(old, new) -> Optional[float]:
    """
    Prozentuale Veränderung.
    Nicht definiert bei altem Wert = 0.
    """
    old = safe_float(old)
    new = safe_float(new)

    if old is None or new is None:
        return None

    if old == 0:
        return None

    return (new / old - 1.0) * 100.0


def format_eur(value: Optional[float]) -> str:
    """
    Geldwerte in EUR.
    """
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
    """
    Liefert näherungsweise den EUR-Wert einer Einheit der
    Unternehmenswährung.

    Wichtig:
    Diese Funktion dient primär der Darstellung.
    Historische Wachstums-/Beschleunigungsberechnungen
    werden weiterhin bevorzugt in der Originalwährung
    durchgeführt, damit Wechselkurse nicht mit operativer
    Beschleunigung verwechselt werden.
    """

    currency = (currency or "EUR").upper()

    if currency == "EUR":
        return 1.0

    if currency == "GBX":
        gbp_rate = get_global_fx_rate("GBP")
        return 0.01 * gbp_rate

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
# BESCHLEUNIGUNG
# ============================================================

def classify_acceleration(series: pd.Series) -> dict:
    """
    Unterscheidet:
      - rückläufig
      - wachsend, aber nicht beschleunigend
      - beschleunigend
      - verlangsamend

    Wichtig:
    Beschleunigung bedeutet hier nicht einfach Wachstum.

    Beispiel:
      Umsatz:
      100 -> 120 -> 145 -> 180

      Deltas:
      +20 -> +25 -> +35

      Die absoluten Zuwächse werden größer.
      Das ist Beschleunigung.

    Die Berechnung erfolgt in der Originalwährung.
    """

    s = clean_series(series)

    result = {
        "status": "Nicht ausreichend Daten",
        "score": 0,
        "deltas": [],
        "delta_changes": [],
        "growth_rates": [],
        "message": "Für eine belastbare Beschleunigungsanalyse fehlen historische Daten."
    }

    if len(s) < 3:
        return result

    values = s.values.astype(float)

    deltas = np.diff(values)

    # Wachstumsraten nur berechnen, wenn die Basis sinnvoll ist.
    growth_rates = []

    for old, new in zip(values[:-1], values[1:]):
        if old != 0:
            growth_rates.append((new / old - 1.0) * 100.0)
        else:
            growth_rates.append(np.nan)

    delta_changes = np.diff(deltas)

    latest_value_ = values[-1]

    # --------------------------------------------------------
    # 1. Umsatz / Kennzahl fällt tatsächlich
    # --------------------------------------------------------
    if latest_value_ < values[-2]:
        result["status"] = "🔴 Rückläufig"
        result["score"] = 20
        result["message"] = (
            "Die jüngste Kennzahl liegt unter dem Vorjahreswert. "
            "Das ist keine Beschleunigung, sondern ein Rückgang."
        )

    # --------------------------------------------------------
    # 2. Zuwächse werden größer
    # --------------------------------------------------------
    elif len(delta_changes) >= 1 and delta_changes[-1] > 0:
        result["status"] = "🟢 Beschleunigend"
        result["score"] = 90
        result["message"] = (
            "Die absoluten Zuwächse werden größer. "
            "Das spricht für eine operative Beschleunigung."
        )

    # --------------------------------------------------------
    # 3. Zuwachs bleibt positiv, wird aber kleiner
    # --------------------------------------------------------
    elif len(delta_changes) >= 1 and delta_changes[-1] < 0:
        result["status"] = "🟠 Verlangsamend"
        result["score"] = 50
        result["message"] = (
            "Die Kennzahl wächst weiterhin, aber der zusätzliche "
            "Zuwachs wird kleiner."
        )

    # --------------------------------------------------------
    # 4. Zuwachs ungefähr konstant
    # --------------------------------------------------------
    else:
        result["status"] = "➡️ Wachsend, nicht beschleunigend"
        result["score"] = 65
        result["message"] = (
            "Die Kennzahl wächst, aber die Zuwächse zeigen "
            "keine klare zusätzliche Beschleunigung."
        )

    result["deltas"] = deltas.tolist()
    result["delta_changes"] = delta_changes.tolist()
    result["growth_rates"] = growth_rates

    return result


# ============================================================
# MARGENTREND
# ============================================================

def calculate_margin_series(
    revenue_series: pd.Series,
    net_income_series: pd.Series
) -> pd.Series:
    """
    Berechnet historische Nettomargen.
    Nur gemeinsame Zeitpunkte werden verwendet.
    """

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

        if rev is None or ni is None or rev == 0:
            continue

        margins[date] = ni / rev * 100.0

    return pd.Series(margins).sort_index()


def classify_margin_trend(margin_series: pd.Series) -> dict:
    """
    Klassifiziert die Margenentwicklung.
    """

    s = clean_series(margin_series)

    result = {
        "status": "Nicht ausreichend Daten",
        "score": 50,
        "message": "Keine belastbare Margen-Zeitreihe verfügbar."
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
            "Die Nettomarge ist zuletzt spürbar gestiegen."
        )

    elif change < -2:
        result["status"] = "🟠 Margen verschlechtern sich"
        result["score"] = 35
        result["message"] = (
            "Die Nettomarge ist zuletzt spürbar gefallen."
        )

    else:
        result["status"] = "➡️ Margen weitgehend stabil"
        result["score"] = 65
        result["message"] = (
            "Die Nettomarge zeigt zuletzt keine starke Veränderung."
        )

    return result


# ============================================================
# FINANZIELLE ZEITREIHEN
# ============================================================

def calculate_fcf(
    operating_cashflow: Optional[pd.Series],
    capex: Optional[pd.Series]
) -> pd.Series:
    """
    Free Cashflow = Operating Cashflow + CapEx

    CapEx ist in Cashflow-Statements normalerweise negativ.
    Deshalb wird bewusst NICHT OCF - CapEx gerechnet.

    Wenn eine der beiden Reihen fehlt, wird kein künstlicher
    FCF erfunden.
    """

    ocf = clean_series(operating_cashflow)
    capex_series = clean_series(capex)

    if ocf.empty or capex_series.empty:
        return pd.Series(dtype=float)

    common_dates = ocf.index.intersection(capex_series.index)

    if len(common_dates) == 0:
        return pd.Series(dtype=float)

    fcf_values = {}

    for date in common_dates:
        ocf_value = safe_float(ocf.loc[date])
        capex_value = safe_float(capex_series.loc[date])

        if ocf_value is None or capex_value is None:
            continue

        fcf_values[date] = ocf_value + capex_value

    return pd.Series(fcf_values).sort_index()


def classify_fcf_dynamics(fcf_series: pd.Series) -> dict:
    """
    Klassifiziert die FCF-Dynamik.

    Bei Wechsel von negativ auf positiv oder umgekehrt wird
    keine irreführende prozentuale Wachstumsrate berechnet.
    """

    s = clean_series(fcf_series)

    result = {
        "status": "Nicht ausreichend Daten",
        "score": 50,
        "message": "Keine ausreichende FCF-Zeitreihe."
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
            "Der Free Cashflow ist zuletzt in den positiven Bereich gedreht."
        )

    elif latest > 0 and previous > 0 and latest > previous:
        result["status"] = "🟢 FCF verbessert sich"
        result["score"] = 85
        result["message"] = (
            "Der positive Free Cashflow hat sich gegenüber dem Vorjahr verbessert."
        )

    elif latest > 0 and previous > 0 and latest < previous:
        result["status"] = "🟠 FCF schwächer"
        result["score"] = 50
        result["message"] = (
            "Der Free Cashflow bleibt positiv, ist aber gegenüber dem Vorjahr gefallen."
        )

    elif latest < 0 and previous < 0 and latest < previous:
        result["status"] = "🔴 FCF-Belastung steigt"
        result["score"] = 20
        result["message"] = (
            "Der negative Free Cashflow ist zuletzt noch negativer geworden."
        )

    else:
        result["status"] = "➡️ FCF uneinheitlich"
        result["score"] = 45
        result["message"] = (
            "Die FCF-Entwicklung lässt sich derzeit nicht eindeutig als Trend einordnen."
        )

    return result


# ============================================================
# EVIDENCE ENGINE
# ============================================================

def calculate_evidence(
    revenue_series: pd.Series,
    ocf_series: pd.Series,
    capex_series: pd.Series,
    shares_series: pd.Series,
    balance_sheet_available: bool,
    cashflow_available: bool,
    financials_available: bool
) -> dict:
    """
    Evidenzscore.

    Der Score bedeutet NICHT:
    "Diese Aktie ist gut."

    Er bedeutet:
    "Wie viel belastbare Finanzinformation kann der Scanner
     aktuell technisch auswerten?"

    Primärquellen werden durch yfinance NICHT automatisch
    verifiziert.
    """

    score = 0
    reasons = []
    warnings = []

    revenue = clean_series(revenue_series)
    ocf = clean_series(ocf_series)
    capex = clean_series(capex_series)
    shares = clean_series(shares_series)

    if not revenue.empty:
        score += 20
        reasons.append("Umsatzdaten vorhanden")
    else:
        warnings.append("Keine verwertbare Umsatzhistorie")

    if not ocf.empty:
        score += 15
        reasons.append("Operativer Cashflow vorhanden")
    else:
        warnings.append("Kein verwertbarer operativer Cashflow")

    if len(revenue) >= 3:
        score += 15
        reasons.append("Mindestens 3 historische Umsatzperioden")

    elif len(revenue) >= 2:
        score += 8
        warnings.append("Nur kurze Umsatzhistorie")

    else:
        warnings.append("Zu wenig Umsatzhistorie")

    if not shares.empty:
        score += 15
        reasons.append("Historische Aktienzahl verfügbar")
    else:
        warnings.append("Historische Aktienzahl nicht zuverlässig verfügbar")

    if not capex.empty:
        score += 10
        reasons.append("CapEx vorhanden")
    else:
        warnings.append("CapEx fehlt – FCF kann dadurch unvollständig sein")

    if financials_available:
        score += 5
        reasons.append("GuV-Daten verfügbar")

    if cashflow_available:
        score += 5
        reasons.append("Cashflow-Daten verfügbar")

    if balance_sheet_available:
        score += 5
        reasons.append("Bilanzdaten verfügbar")

    # Kein künstliches Aufblasen.
    score = min(score, 100)

    if score >= 85:
        level = "🟢 Gute Datengrundlage"
    elif score >= 65:
        level = "🟡 Brauchbare, aber lückenhafte Datengrundlage"
    elif score >= 45:
        level = "🟠 Schwache Datengrundlage"
    else:
        level = "🔴 Scanner versteht den Fall noch nicht ausreichend"

    return {
        "score": score,
        "level": level,
        "reasons": reasons,
        "warnings": warnings,
        "primary_sources_verified": False
    }


# ============================================================
# CAPITAL & DILUTION DETECTIVE
# ============================================================

def analyze_dilution(
    shares_series: pd.Series,
    revenue_series: pd.Series,
    fcf_series: pd.Series
) -> dict:
    """
    Aktienzahlentwicklung != automatisch Verwässerung.

    Eine steigende Aktienzahl kann entstehen durch:
      - Kapitalerhöhung
      - Aktienvergütung
      - Akquisitionen
      - Optionen / RSUs
      - Convertibles
      - andere Kapitalmaßnahmen
      - technische / historische Datenänderungen

    Deshalb sprechen wir bewusst von:
    "Aktienzahlentwicklung" und "Verwässerungsdruck",
    solange die Ursache nicht bekannt ist.
    """

    shares = clean_series(shares_series)
    revenue = clean_series(revenue_series)
    fcf = clean_series(fcf_series)

    result = {
        "status": "Nicht ausreichend Daten",
        "message": "Keine belastbare Aktienzahlhistorie.",
        "share_change_pct": None,
        "revenue_change_pct": None,
        "fcf_change_pct": None,
        "share_start": None,
        "share_end": None
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
        result["revenue_change_pct"] = percent_change(
            revenue.iloc[0],
            revenue.iloc[-1]
        )

    if len(fcf) >= 2:
        # Nur darstellen, nicht blind als Wachstum interpretieren.
        old_fcf = safe_float(fcf.iloc[0])
        new_fcf = safe_float(fcf.iloc[-1])

        if (
            old_fcf is not None
            and new_fcf is not None
            and old_fcf > 0
        ):
            result["fcf_change_pct"] = percent_change(
                old_fcf,
                new_fcf
            )

    if share_change is None:
        return 
