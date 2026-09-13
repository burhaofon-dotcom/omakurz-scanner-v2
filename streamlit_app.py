import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="OmaKurz™ Scanner v2.2",
    page_icon="🧭",
    layout="centered"
)

st.title("🧭 OMAKURZ™ SCANNER v2.2")
st.caption(
    "Financing Detective • Dilution Delta • True Acceleration • "
    "Pipeline & Story/Reality Framework"
)

ticker_symbol = st.text_input(
    "Börsenkürzel / Ticker eingeben (z.B. OSPN, ALNY, RTO.L):",
    "OSPN"
).upper().strip()


# ============================================================
# HILFSFUNKTIONEN
# ============================================================

def safe_float(value, default=np.nan):
    try:
        if value is None:
            return default
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def find_row(df, candidates):
    """Findet möglichst robuste Zeilen in yfinance DataFrames."""
    if df is None or df.empty:
        return None

    for candidate in candidates:
        for row in df.index:
            row_str = str(row).lower()
            if candidate.lower() in row_str:
                return row

    return None


def clean_series(series):
    """Entfernt fehlende Werte und sortiert chronologisch."""
    if series is None:
        return pd.Series(dtype=float)

    try:
        s = pd.to_numeric(series, errors="coerce").dropna()

        if len(s) == 0:
            return pd.Series(dtype=float)

        # yfinance liefert meist neuestes Jahr zuerst.
        # Wir wollen alt -> neu.
        return s.iloc[::-1]
    except Exception:
        return pd.Series(dtype=float)


def format_money(value):
    if pd.isna(value):
        return "n/a"

    abs_value = abs(value)

    if abs_value >= 1:
        return f"{value:.2f} Mrd."
    return f"{value * 1000:.0f} Mio."


def classify_acceleration(series):
    """
    Unterscheidet:
    - Rückläufig
    - Beschleunigend
    - Linear / stabil
    - Verlangsamend
    """

    s = clean_series(series)

    if len(s) < 4:
        return {
            "label": "⚪ Keine ausreichende Historie",
            "score": 60,
            "deltas": [],
            "growth_rates": []
        }

    vals = s.values.astype(float)

    deltas = np.diff(vals)

    growth_rates = []

    for i in range(1, len(vals)):
        previous = vals[i - 1]

        if previous != 0:
            growth_rates.append((vals[i] / previous) - 1)
        else:
            growth_rates.append(np.nan)

    # Umsatz selbst fällt
    if vals[-1] < vals[-2]:
        label = "🔴 Rückläufig"
        score = 25

    else:
        # Veränderung der absoluten Zuwächse
        delta_change = deltas[-1] - deltas[-2]

        # Toleranz relativ zum vorherigen Delta
        reference = max(abs(deltas[-2]), 1)

        tolerance = reference * 0.05

        if delta_change > tolerance:
            label = "🟢 Beschleunigend"
            score = 90

        elif abs(delta_change) <= tolerance:
            label = "➡️ Wachsend, aber ungefähr linear"
            score = 70

        else:
            label = "🟠 Verlangsamend"
            score = 45

    return {
        "label": label,
        "score": score,
        "deltas": deltas.tolist(),
        "growth_rates": growth_rates
    }


def growth_comparison(start, end):
    """
    Vergleich zweier Größen.
    Gibt relative Veränderung zurück.
    """

    if pd.isna(start) or pd.isna(end) or start == 0:
        return np.nan

    return ((end / start) - 1) * 100


# ============================================================
# ENGINE
# ============================================================

if st.button("⚡ OmaKurz v2.2 starten"):

    try:

        # ====================================================
        # DATEN LADEN
        # ====================================================

        stock = yf.Ticker(ticker_symbol)

        info = stock.info

        company_name = info.get("longName", ticker_symbol)
        sector = info.get("sector", "Unbekannt")

        current_price = safe_float(
            info.get("currentPrice", info.get("regularMarketPrice"))
        )

        market_cap = safe_float(info.get("marketCap"))

        total_cash = safe_float(info.get("totalCash"))
        total_debt = safe_float(info.get("totalDebt"))

        if pd.isna(total_cash):
            total_cash = 0

        if pd.isna(total_debt):
            total_debt = 0

        net_cash = total_cash - total_debt

        rev_growth = safe_float(info.get("revenueGrowth"))
        profit_margin = safe_float(info.get("profitMargins"))

        if not pd.isna(rev_growth):
            rev_growth *= 100

        if not pd.isna(profit_margin):
            profit_margin *= 100

        # Finanzberichte
        try:
            financials = stock.financials
        except Exception:
            financials = pd.DataFrame()

        try:
            cashflow = stock.cashflow
        except Exception:
            cashflow = pd.DataFrame()

        try:
            balance_sheet = stock.balance_sheet
        except Exception:
            balance_sheet = pd.DataFrame()


        # ====================================================
        # 1. EVIDENCE ENGINE
        # ====================================================

        revenue_row = find_row(
            financials,
            ["Total Revenue", "Operating Revenue"]
        )

        ocf_row = find_row(
            cashflow,
            ["Operating Cash Flow", "Total Cash From Operating Activities"]
        )

        capex_row = find_row(
            cashflow,
            [
                "Capital Expenditure",
                "Capital Expenditure Reported",
                "Purchase Of Property Plant And Equipment"
            ]
        )

        net_income_row = find_row(
            financials,
            ["Net Income"]
        )

        # Share Count:
        # ABSICHTLICH KEIN "Common Stock"
        share_row = find_row(
            balance_sheet,
            [
                "Ordinary Shares Number",
                "Share Issued"
            ]
        )

        revenue_series = clean_series(
            financials.loc[revenue_row]
            if revenue_row is not None
            else None
        )

        ocf_series = clean_series(
            cashflow.loc[ocf_row]
            if ocf_row is not None
            else None
        )

        capex_series = clean_series(
            cashflow.loc[capex_row]
            if capex_row is not None
            else None
        )

        net_income_series = clean_series(
            financials.loc[net_income_row]
            if net_income_row is not None
            else None
        )

        shares_series = clean_series(
            balance_sheet.loc[share_row]
            if share_row is not None
            else None
        )

        has_revenue = len(revenue_series) > 0
        has_ocf = len(ocf_series) > 0
        has_hist = len(revenue_series) >= 3
        has_shares = len(shares_series) >= 2
        has_capex = len(capex_series) > 0

        evidence_score = 30

        if has_revenue:
            evidence_score += 15

        if has_ocf:
            evidence_score += 15

        if has_hist:
            evidence_score += 15

        if has_shares:
            evidence_score += 10

        if has_capex:
            evidence_score += 5

        evidence_score = min(evidence_score, 100)

        st.markdown("### 🔍 Evidence & Datenabdeckung")

        e1, e2 = st.columns(2)

        with e1:
            st.write(
                f"• Umsatzdaten: "
                f"{'🟢 Vorhanden' if has_revenue else '🔴 Fehlt'}"
            )

            st.write(
                f"• Historie: "
                f"{'🟢 3+ Jahre' if has_hist else '🟡 Begrenzt'}"
            )

            st.write(
                f"• OCF: "
                f"{'🟢 Vorhanden' if has_ocf else '🔴 Fehlt'}"
            )

        with e2:
            st.write(
                f"• Aktienhistorie: "
                f"{'🟢 Vorhanden' if has_shares else '🟡 Nicht ausreichend'}"
            )

            st.write(
                f"• CapEx: "
                f"{'🟢 Vorhanden' if has_capex else '🟡 Fehlt'}"
            )

            st.write("• Pipeline: ⚪ Noch nicht verifiziert")
            st.write("• Primärquellen: ⚪ Noch nicht verifiziert")

        st.caption(
            f"Transparenz-/Datenabdeckungsindex: "
            f"{evidence_score}/100"
        )


        # ====================================================
        # 2. FCF ENGINE
        # ====================================================

        fcf_series = pd.Series(dtype=float)

        if has_ocf and has_capex:

            try:
                combined = pd.concat(
                    [
                        ocf_series.rename("OCF"),
                        capex_series.rename("CapEx")
                    ],
                    axis=1
                ).dropna()

                if not combined.empty:
                    # CapEx ist bei yfinance normalerweise negativ.
                    # Daher OCF + CapEx.
                    fcf_series = combined["OCF"] + combined["CapEx"]

            except Exception:
                fcf_series = pd.Series(dtype=float)


        # ====================================================
        # 3. TRUE DELTA ACCELERATION
        # ====================================================

        acceleration = classify_acceleration(revenue_series)

        rev_accel_label = acceleration["label"]
        accel_score = acceleration["score"]

        st.markdown("### ⚡ True Delta Acceleration")

        if len(revenue_series) >= 4:

            history_text = " → ".join(
                format_money(v / 1e9)
                for v in revenue_series.values
            )

            st.write(
                f"**Umsatz:** {history_text}"
            )

            deltas = acceleration["deltas"]

            delta_text = " → ".join(
                format_money(v / 1e9)
                for v in deltas
            )

            st.write(
                f"**Jährliche Zuwächse:** {delta_text}"
            )

            st.write(
                f"**Dynamik:** {rev_accel_label}"
            )

        else:

            st.warning(
                "Für eine belastbare Beschleunigungsanalyse "
                "liegen zu wenige historische Umsatzdaten vor."
            )


        # ====================================================
        # 4. FCF DYNAMIK
        # ====================================================

        fcf_label = "⚪ Nicht ausreichend"

        if len(fcf_series) >= 3:

            fcf_values = fcf_series.values

            if fcf_values[-1] < 0:

                if fcf_values[-2] < fcf_values[-1]:
                    fcf_label = "🟠 Cash Burn bleibt problematisch"

                else:
                    fcf_label = "🟡 Cash Burn verbessert sich"

            else:

                if fcf_values[-1] > fcf_values[-2]:
                    fcf_label = "🟢 FCF verbessert sich"

                elif fcf_values[-1] < fcf_values[-2]:
                    fcf_label = "🟠 FCF verschlechtert sich"

                else:
                    fcf_label = "➡️ FCF ungefähr stabil"

        st.write(f"**FCF-Dynamik:** {fcf_label}")


        # ====================================================
        # 5. CAPITAL & DILUTION DETECTIVE
        # ====================================================

        st.markdown("### 🕵️ Capital & Dilution Detective")

        dilution_score = 50

        share_change_pct = np.nan
        revenue_change_pct = np.nan
        fcf_change_pct = np.nan

        if has_shares:

            s_start = shares_series.iloc[0]
            s_end = shares_series.iloc[-1]

            share_change_pct = growth_comparison(
                s_start,
                s_end
            )

            st.write(
                f"**Aktienzahl:** "
                f"{s_start / 1e6:.1f} Mio. → "
                f"{s_end / 1e6:.1f} Mio. "
                f"({share_change_pct:+.1f}%)"
            )

        else:

            st.write(
                "🟡 Keine ausreichende Aktienhistorie verfügbar."
            )


        if len(revenue_series) >= 2:

            revenue_change_pct = growth_comparison(
                revenue_series.iloc[0],
                revenue_series.iloc[-1]
            )

            st.write(
                f"**Umsatz über denselben Zeitraum:** "
                f"{revenue_change_pct:+.1f}%"
            )


        if len(fcf_series) >= 2:

            fcf_start = fcf_series.iloc[0]
            fcf_end = fcf_series.iloc[-1]

            # Keine sinnlose Prozentrechnung bei negativem Startwert.
            if fcf_start > 0:

                fcf_change_pct = growth_comparison(
                    fcf_start,
                    fcf_end
                )

                st.write(
                    f"**FCF über denselben Zeitraum:** "
                    f"{fcf_change_pct:+.1f}%"
                )

            else:

                st.write(
                    "**FCF:** Ausgangswert negativ – "
                    "kein irreführender Wachstumsprozentsatz."
                )


        # ====================================================
        # DILUTION DELTA INTERPRETATION
        # ====================================================

        if not pd.isna(share_change_pct):

            if share_change_pct > 10:

                if (
                    not pd.isna(revenue_change_pct)
                    and revenue_change_pct < share_change_pct
                ):

                    dilution_delta_text = (
                        "🔴 Aktienzahl wächst deutlich schneller "
                        "als der Umsatz."
                    )

                    dilution_score = 25

                else:

                    dilution_delta_text = (
                        "🟡 Aktienzahl deutlich gestiegen – "
                        "wirtschaftliche Gegenleistung prüfen."
                    )

                    dilution_score = 45

            elif share_change_pct > 3:

                dilution_delta_text = (
                    "🟡 Aktienzahl moderat gestiegen – "
                    "Ursache muss geprüft werden."
                )

                dilution_score = 60

            else:

                dilution_delta_text = (
                    "🟢 Aktienzahl relativ stabil."
                )

                dilution_score = 85

        else:

            dilution_delta_text = (
                "⚪ Keine ausreichende Aktienhistorie."
            )

        st.write(
            f"**Dilution Delta:** {dilution_delta_text}"
        )

        st.caption(
            "Wichtig: Eine steigende Aktienzahl ist noch kein Beweis "
            "für Verwässerung. Ursache muss separat geprüft werden."
        )


        # ====================================================
        # 6. FINANCING DETECTIVE
        # ====================================================

        st.markdown("### 💰 Finanzierungs-Detektiv")

        op_cashflow_current = (
            ocf_series.iloc[-1] / 1e9
            if len(ocf_series) > 0
            else np.nan
        )

        fcf_current = (
            fcf_series.iloc[-1] / 1e9
            if len(fcf_series) > 0
            else np.nan
        )

        cash_burn = np.nan
        runway_years = np.nan

        if not pd.isna(fcf_current) and fcf_current < 0:

            cash_burn = abs(fcf_current)

            if total_cash > 0:

                runway_years = total_cash / (
                    cash_burn * 1e9
                )

        st.write(
            f"• **Cash:** {format_money(total_cash / 1e9)}"
        )

        st.write(
            f"• **Debt:** {format_money(total_debt / 1e9)}"
        )

        st.write(
            f"• **Netto-Cash:** "
            f"{format_money(net_cash / 1e9)}"
        )

        if not pd.isna(op_cashflow_current):

            st.write(
                f"• **Operativer Cashflow:** "
                f"{format_money(op_cashflow_current)}"
            )

        if not pd.isna(fcf_current):

            st.write(
                f"• **Free Cashflow:** "
                f"{format_money(fcf_current)}"
            )

        if not pd.isna(runway_years):

            if runway_years < 2:

                st.error(
                    f"🚨 Rechnerische Cash-Runway nur ca. "
                    f"{runway_years:.1f} Jahre."
                )

            elif runway_years < 4:

                st.warning(
                    f"🟡 Rechnerische Cash-Runway ca. "
                    f"{runway_years:.1f} Jahre."
                )

            else:

                st.success(
                    f"🟢 Rechnerische Cash-Runway ca. "
                    f"{runway_years:.1f} Jahre."
                )

        elif not pd.isna(fcf_current) and fcf_current >= 0:

            st.success(
                "🟢 Aktuell kein negativer FCF-Cash-Burn."
            )

        else:

            st.info(
                "⚪ Runway nicht zuverlässig berechenbar."
            )


        # ====================================================
        # 7. OMA SUBSTANZ
        # ====================================================

        oma_substanz = 20

        if net_cash > 0:
            oma_substanz += 35

        elif net_cash > -2e9:
            oma_substanz += 15

        if not pd.isna(op_cashflow_current):

            if op_cashflow_current > 0:
                oma_substanz += 25

            elif op_cashflow_current > -0.5:
                oma_substanz += 10

        if not pd.isna(fcf_current):

            if fcf_current > 0:
                oma_substanz += 20

        oma_substanz = min(oma_substanz, 100)


        # ====================================================
        # 8. KURZ ZUKUNFT
        # ====================================================

        kurz_zukunft = 20

        if not pd.isna(rev_growth):

            if rev_growth > 20:
                kurz_zukunft += 40

            elif rev_growth > 10:
                kurz_zukunft += 25

            elif rev_growth > 5:
                kurz_zukunft += 15

        if not pd.isna(profit_margin):

            if profit_margin > 15:
                kurz_zukunft += 30

            elif profit_margin > 0:
                kurz_zukunft += 15

        kurz_zukunft = min(kurz_zukunft, 100)


        # ====================================================
        # 9. PIPELINE FRAMEWORK
        # ====================================================

        st.markdown("### 🧬 Pipeline")

        st.info(
            "v2.2 erkennt Pipeline-Relevanz, verifiziert aber noch "
            "keine klinischen Phasen oder Entwicklungsprogramme "
            "automatisch. Dafür müssen Unternehmensangaben und "
            "Primärquellen eingebunden werden."
        )

        pipeline_score = None


        # ====================================================
        # 10. STORY vs REALITY
        # ====================================================

        st.markdown("### 📰 Story vs. Reality")

        story_checks = []

        if not pd.isna(rev_growth):

            if rev_growth > 20:
                story_checks.append(
                    "🟢 Umsatz bestätigt zumindest einen Teil der Wachstumsstory."
                )

            elif rev_growth > 0:
                story_checks.append(
                    "🟡 Umsatz wächst – aber nicht außergewöhnlich stark."
                )

            else:
                story_checks.append(
                    "🔴 Umsatz bestätigt keine aktuelle Wachstumsstory."
                )

        if not pd.isna(fcf_current):

            if fcf_current > 0:
                story_checks.append(
                    "🟢 FCF liefert reale finanzielle Unterstützung."
                )

            else:
                story_c
