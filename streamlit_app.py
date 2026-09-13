# ============================================================
# OmaKurz™ Scanner
# Datei: omakurz_helpers.py
# ============================================================

from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st
import omakurz_analysis
import yfinance as yf


def safe_float(value) -> Optional[float]:
    """Versucht einen Wert sicher in float umzuwandeln."""
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except Exception:
        pass

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def clean_series(series) -> pd.Series:
    """Bereinigt eine Pandas-Zeitreihe."""
    if series is None:
        return pd.Series(dtype=float)

    if not isinstance(series, pd.Series):
        try:
            series = pd.Series(series)
        except Exception:
            return pd.Series(dtype=float)

    result = pd.to_numeric(series, errors="coerce")
    result = result.dropna()

    try:
        result = result.sort_index()
    except Exception:
        pass

    return result


def find_row(
    dataframe: Optional[pd.DataFrame],
    exact_names=None,
    contains_names=None,
) -> Optional[pd.Series]:
    """Sucht eine Zeile anhand exakter oder teilweiser Namen."""
    if dataframe is None:
        return None

    if not isinstance(dataframe, pd.DataFrame):
        return None

    if dataframe.empty:
        return None

    if exact_names is None:
        exact_names = []

    if contains_names is None:
        contains_names = []

    for name in exact_names:
        target = str(name).strip().lower()

        for index in dataframe.index:
            if str(index).strip().lower() == target:
                return dataframe.loc[index]

    for name in contains_names:
        target = str(name).strip().lower()

        for index in dataframe.index:
            if target in str(index).strip().lower():
                return dataframe.loc[index]

    return None
    def latest_value(series) -> Optional[float]:
    """Liefert den jüngsten numerischen Wert einer Zeitreihe."""
    cleaned = clean_series(series)

    if cleaned.empty:
        return None

    try:
        return safe_float(cleaned.iloc[-1])
    except Exception:
        return None


def first_value(series) -> Optional[float]:
    """Liefert den ältesten numerischen Wert einer Zeitreihe."""
    cleaned = clean_series(series)

    if cleaned.empty:
        return None

    try:
        return safe_float(cleaned.iloc[0])
    except Exception:
        return None


def percent_change(
    current: Optional[float],
    previous: Optional[float],
) -> Optional[float]:
    """Berechnet die prozentuale Veränderung."""
    current_value = safe_float(current)
    previous_value = safe_float(previous)

    if current_value is None or previous_value is None:
        return None

    if previous_value == 0:
        return None

    return (
        (current_value - previous_value)
        / abs(previous_value)
    ) * 100.0


def absolute_change(
    current: Optional[float],
    previous: Optional[float],
) -> Optional[float]:
    """Berechnet die absolute Veränderung."""
    current_value = safe_float(current)
    previous_value = safe_float(previous)

    if current_value is None or previous_value is None:
        return None

    return current_value - previous_value


def format_number(
    value: Optional[float],
    decimals: int = 1,
    fallback: str = "n. a.",
) -> str:
    """Formatiert eine Zahl für die Benutzeroberfläche."""
    number = safe_float(value)

    if number is None:
        return fallback

    formatted = (
        f"{number:,.{decimals}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return formatted


def format_percent(
    value: Optional[float],
    decimals: int = 1,
    fallback: str = "n. a.",
) -> str:
    """Formatiert einen Prozentwert."""
    number = safe_float(value)

    if number is None:
        return fallback

    formatted = (
        f"{number:,.{decimals}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"{formatted}%"


def format_eur(
    value: Optional[float],
    decimals: int = 0,
    fallback: str = "n. a.",
) -> str:
    """Formatiert einen EUR-Betrag."""
    number = safe_float(value)

    if number is None:
        return fallback

    formatted = (
        f"{number:,.{decimals}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"{formatted} €"
    def format_currency(
    value: Optional[float],
    currency: str = "EUR",
    decimals: int = 0,
    fallback: str = "n. a.",
) -> str:
    """Formatiert einen Geldbetrag mit Währungskürzel."""
    number = safe_float(value)

    if number is None:
        return fallback

    formatted = (
        f"{number:,.{decimals}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"{formatted} {currency}"


def format_multiple(
    value: Optional[float],
    decimals: int = 1,
    fallback: str = "n. a.",
) -> str:
    """Formatiert einen Multiplikator."""
    number = safe_float(value)

    if number is None:
        return fallback

    formatted = (
        f"{number:,.{decimals}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"{formatted}x"


def get_financial_statement(
    ticker: yf.Ticker,
    statement_name: str,
) -> pd.DataFrame:
    """Holt eine Finanz-Tabelle von yfinance."""
    try:
        if statement_name == "income_stmt":
            dataframe = ticker.income_stmt

        elif statement_name == "financials":
            dataframe = ticker.financials

        elif statement_name == "balance_sheet":
            dataframe = ticker.balance_sheet

        elif statement_name == "cashflow":
            dataframe = ticker.cashflow

        else:
            return pd.DataFrame()

        if dataframe is None:
            return pd.DataFrame()

        if not isinstance(dataframe, pd.DataFrame):
            return pd.DataFrame()

        return dataframe.copy()

    except Exception:
        return pd.DataFrame()


def get_company_currency(
    ticker: yf.Ticker,
    info: Optional[dict] = None,
) -> str:
    """Versucht die Berichtswährung des Unternehmens zu bestimmen."""
    if info is not None:
        try:
            currency = info.get("currency")

            if currency:
                return str(currency).upper()
        except Exception:
            pass

    try:
        fast_info = ticker.fast_info

        if fast_info is not None:
            currency = fast_info.get("currency")

            if currency:
                return str(currency).upper()

    except Exception:
        pass

    return "UNKNOWN"


def normalize_currency(
    currency: Optional[str],
) -> str:
    """Vereinheitlicht einfache Währungsbezeichnungen."""
    if currency is None:
        return "UNKNOWN"

    value = str(currency).strip().upper()

    mapping = {
        "EURO": "EUR",
        "€": "EUR",
        "US DOLLAR": "USD",
        "$": "USD",
        "POUND": "GBP",
        "£": "GBP",
    }

    return mapping.get(value, value)
    @st.cache_data(ttl=3600, show_spinner=False)
def get_global_fx_rate(
    from_currency: str,
    to_currency: str = "EUR",
) -> Optional[float]:
    """
    Holt einen aktuellen Wechselkurs über Yahoo Finance.

    Der Kurs dient vor allem zur Darstellung in EUR.
    Historische operative Vergleiche sollten möglichst
    in der jeweiligen Originalwährung erfolgen.
    """
    if not from_currency:
        return None

    source = str(from_currency).upper().strip()
    target = str(to_currency).upper().strip()

    if source == target:
        return 1.0

    pair = f"{source}{target}=X"

    try:
        fx_ticker = yf.Ticker(pair)
        history = fx_ticker.history(period="5d")

        if history is None or history.empty:
            return None

        if "Close" not in history.columns:
            return None

        close_series = clean_series(history["Close"])

        if close_series.empty:
            return None

        return latest_value(close_series)

    except Exception:
        return None


def convert_to_eur(
    value: Optional[float],
    from_currency: str,
) -> Optional[float]:
    """Konvertiert einen Betrag anhand des aktuellen FX-Kurses in EUR."""
    number = safe_float(value)

    if number is None:
        return None

    currency = normalize_currency(from_currency)

    if currency == "EUR":
        return number

    fx_rate = get_global_fx_rate(currency, "EUR")

    if fx_rate is None:
        return None

    return number * fx_rate


def find_share_row(
    balance_sheet: Optional[pd.DataFrame],
) -> Optional[pd.Series]:
    """
    Sucht gezielt nach einer Aktienanzahl.

    'Common Stock' wird bewusst nicht als Aktienanzahl verwendet,
    weil es sich dabei um einen Bilanzwert handeln kann.
    """
    if balance_sheet is None:
        return None

    row = find_row(
        balance_sheet,
        exact_names=[
            "Ordinary Shares Number",
            "Share Issued",
        ],
    )

    if row is not None:
        return row

    row = find_row(
        balance_sheet,
        contains_names=[
            "Ordinary Shares Number",
            "Share Issued",
        ],
    )

    return row


def get_share_series(
    balance_sheet: Optional[pd.DataFrame],
) -> pd.Series:
    """Liefert die bereinigte Zeitreihe der gemeldeten Aktienanzahl."""
    row = find_share_row(balance_sheet)

    if row is None:
        return pd.Series(dtype=float)

    return clean_series(row)


def get_latest_shares(
    balance_sheet: Optional[pd.DataFrame],
) -> Optional[float]:
    """Liefert die zuletzt gemeldete Aktienanzahl."""
    shares = get_share_series(balance_sheet)

    if shares.empty:
        return None

    return latest_value(shares)


def get_previous_shares(
    balance_sheet: Optional[pd.DataFrame],
) -> Optional[float]:
    """Liefert die zweitjüngste gemeldete Aktienanzahl."""
    shares = get_share_series(balance_sheet)

    if len(shares) < 2:
        return None

    try:
        return safe_float(shares.iloc[-2])
    except Exception:
        return None
        def get_revenue_series(
    income_statement: Optional[pd.DataFrame],
) -> pd.Series:
    """Holt die Umsatz-Zeitreihe."""
    row = find_row(
        income_statement,
        exact_names=[
            "Total Revenue",
            "Operating Revenue",
        ],
    )

    if row is None:
        row = find_row(
            income_statement,
            contains_names=[
                "Total Revenue",
                "Operating Revenue",
            ],
        )

    if row is None:
        return pd.Series(dtype=float)

    return clean_series(row)


def get_net_income_series(
    income_statement: Optional[pd.DataFrame],
) -> pd.Series:
    """Holt die Nettoergebnis-Zeitreihe."""
    row = find_row(
        income_statement,
        exact_names=[
            "Net Income",
            "Net Income Common Stockholders",
        ],
    )

    if row is None:
        row = find_row(
            income_statement,
            contains_names=[
                "Net Income Common Stockholders",
                "Net Income",
            ],
        )

    if row is None:
        return pd.Series(dtype=float)

    return clean_series(row)


def get_operating_cash_flow_series(
    cashflow_statement: Optional[pd.DataFrame],
) -> pd.Series:
    """Holt die operative Cashflow-Zeitreihe."""
    row = find_row(
        cashflow_statement,
        exact_names=[
            "Operating Cash Flow",
            "Total Cash From Operating Activities",
        ],
    )

    if row is None:
        row = find_row(
            cashflow_statement,
            contains_names=[
                "Operating Cash Flow",
                "Total Cash From Operating Activities",
            ],
        )

    if row is None:
        return pd.Series(dtype=float)

    return clean_series(row)


def get_capex_series(
    cashflow_statement: Optional[pd.DataFrame],
) -> pd.Series:
    """Holt die CapEx-Zeitreihe."""
    row = find_row(
        cashflow_statement,
        exact_names=[
            "Capital Expenditure",
        ],
    )

    if row is None:
        row = find_row(
            cashflow_statement,
            contains_names=[
                "Capital Expenditure",
            ],
        )

    if row is None:
        return pd.Series(dtype=float)

    return clean_series(row)


def calculate_fcf(
    operating_cash_flow: Optional[float],
    capex: Optional[float],
) -> Optional[float]:
    """
    Berechnet den Free Cash Flow.

    Bei yfinance wird CapEx häufig negativ dargestellt.

    Deshalb:
        FCF = OCF + CapEx

    Beispiel:
        OCF = 100
        CapEx = -30
        FCF = 70
    """
    ocf = safe_float(operating_cash_flow)
    capex_value = safe_float(capex)

    if ocf is None or capex_value is None:
        return None

    return ocf + capex_value


def get_cash_series(
    balance_sheet: Optional[pd.DataFrame],
) -> pd.Series:
    """Holt die verfügbare Liquidität."""
    row = find_row(
        balance_sheet,
        exact_names=[
            "Cash Cash Equivalents And Short Term Investments",
            "Cash And Cash Equivalents",
        ],
    )

    if row is None:
        row = find_row(
            balance_sheet,
            contains_names=[
                "Cash Cash Equivalents And Short Term Investments",
                "Cash And Cash Equivalents",
            ],
        )

    if row is None:
        return pd.Series(dtype=float)

    return clean_series(row)


def get_debt_series(
    balance_sheet: Optional[pd.DataFrame],
) -> pd.Series:
    """Holt die Gesamtverschuldung."""
    row = find_row(
        balance_sheet,
        exact_names=[
            "Total Debt",
        ],
    )

    if row is None:
        row = find_row(
            balance_sheet,
            contains_names=[
                "Total Debt",
            ],
        )

    if row is None:
        return pd.Series(dtype=float)

    return clean_series(row)
    def get_financing_cash_flow_series(
    cashflow_statement: Optional[pd.DataFrame],
) -> pd.Series:
    """Holt den Cashflow aus Finanzierungstätigkeit."""
    row = find_row(
        cashflow_statement,
        exact_names=[
            "Financing Cash Flow",
            "Total Cash From Financing Activities",
        ],
    )

    if row is None:
        row = find_row(
            cashflow_statement,
            contains_names=[
                "Financing Cash Flow",
                "Total Cash From Financing Activities",
            ],
        )

    if row is None:
        return pd.Series(dtype=float)

    return clean_series(row)


def get_net_cash(
    cash: Optional[float],
    debt: Optional[float],
) -> Optional[float]:
    """
    Berechnet Net Cash.

    Net Cash = Cash - Debt
    """
    cash_value = safe_float(cash)
    debt_value = safe_float(debt)

    if cash_value is None or debt_value is None:
        return None

    return cash_value - debt_value


def get_last_two_values(
    series: Optional[pd.Series],
):
    """
    Liefert die beiden jüngsten Werte einer Zeitreihe.

    Rückgabe:
        (current, previous)
    """
    cleaned = clean_series(series)

    if len(cleaned) < 2:
        return None, None

    return (
        safe_float(cleaned.iloc[-1]),
        safe_float(cleaned.iloc[-2]),
    )


def get_last_three_values(
    series: Optional[pd.Series],
):
    """
    Liefert die drei jüngsten Werte einer Zeitreihe.

    Rückgabe:
        (current, previous, older)
    """
    cleaned = clean_series(series)

    if len(cleaned) < 3:
        return None, None, None

    return (
        safe_float(cleaned.iloc[-1]),
        safe_float(cleaned.iloc[-2]),
        safe_float(cleaned.iloc[-3]),
    )


def calculate_growth_rate_series(
    series: Optional[pd.Series],
) -> pd.Series:
    """
    Berechnet die Wachstumsrate zwischen aufeinanderfolgenden
    Perioden.
    """
    cleaned = clean_series(series)

    if len(cleaned) < 2:
        return pd.Series(dtype=float)

    growth = cleaned.pct_change() * 100.0

    growth = growth.replace(
        [np.inf, -np.inf],
        np.nan,
    ).dropna()

    return growth


def calculate_acceleration_series(
    series: Optional[pd.Series],
) -> pd.Series:
    """
    Berechnet die Veränderung der Wachstumsrate.

    Beispiel:

        Umsatz:
        100 -> 120 -> 150

        Wachstum:
        +20 % -> +25 %

        Beschleunigung:
        +5 Prozentpunkte

    Das ist operative Beschleunigung und kein Kursmomentum.
    """
    growth = calculate_growth_rate_series(series)

    if len(growth) < 2:
        return pd.Series(dtype=float)

    acceleration = growth.diff()

    acceleration = acceleration.replace(
        [np.inf, -np.inf],
        np.nan,
    ).dropna()

    return acceleration
    def get_ticker_info(
    ticker: yf.Ticker,
) -> dict:
    """Holt die Unternehmensinformationen von yfinance."""
    try:
        info = ticker.info

        if isinstance(info, dict):
            return info

    except Exception:
        pass

    return {}


def get_current_price(
    ticker: yf.Ticker,
    info: Optional[dict] = None,
) -> Optional[float]:
    """
    Ermittelt möglichst robust den aktuellen bzw. letzten Kurs.
    """
    if info is not None:
        possible_keys = [
            "currentPrice",
            "regularMarketPrice",
            "previousClose",
        ]

        for key in possible_keys:
            value = safe_float(info.get(key))

            if value is not None:
                return value

    try:
        fast_info = ticker.fast_info

        if fast_info is not None:
            value = safe_float(
                fast_info.get("lastPrice")
            )

            if value is not None:
                return value

    except Exception:
        pass

    try:
        history = ticker.history(period="5d")

        if history is not None and not history.empty:
            if "Close" in history.columns:
                close_series = clean_series(history["Close"])

                if not close_series.empty:
                    return latest_value(close_series)

    except Exception:
        pass

    return None


def calculate_market_cap(
    price: Optional[float],
    shares: Optional[float],
) -> Optional[float]:
    """
    Berechnet die Marktkapitalisierung.

    Market Cap = Aktienkurs × Aktienanzahl
    """
    price_value = safe_float(price)
    shares_value = safe_float(shares)

    if price_value is None or shares_value is None:
        return None

    return price_value * shares_value


def calculate_enterprise_value(
    market_cap: Optional[float],
    debt: Optional[float],
    cash: Optional[float],
) -> Optional[float]:
    """
    Vereinfachte Enterprise-Value-Berechnung.

    EV = Market Cap + Debt - Cash
    """
    market_cap_value = safe_float(market_cap)
    debt_value = safe_float(debt)
    cash_value = safe_float(cash)

    if (
        market_cap_value is None
        or debt_value is None
        or cash_value is None
    ):
        return None

    return (
        market_cap_value
        + debt_value
        - cash_value
    )


def count_available_values(
    *values,
) -> int:
    """Zählt vorhandene numerische Werte."""
    count = 0

    for value in values:
        if safe_float(value) is not None:
            count += 1

    return count


def has_meaningful_series(
    series: Optional[pd.Series],
    minimum_values: int = 2,
) -> bool:
    """Prüft, ob eine Zeitreihe genügend Datenpunkte besitzt."""
    if series is None:
        return False

    cleaned = clean_series(series)

    return len(cleaned) >= minimum_values


def safe_text(
    value,
    fallback: str = "n. a.",
) -> str:
    """Wandelt einen Wert sicher in Text um."""
    if value is None:
        return fallback

    text = str(value).strip()

    if not text:
        return fallback

    return text
    # ============================================================
# ENDE DER DATEI
# ============================================================
