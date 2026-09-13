import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="OmaKurz™ Scanner v2.2.2",
    page_icon="🧭",
    layout="centered"
)

st.title("🧭 OMAKURZ™ SCANNER v2.2.2")
st.caption(
    "Financing Detective • Dilution Delta • True Acceleration • "
    "Kronjuwelen & 1.000€ Beate-Sandler-Geist"
)

col_t1, col_t2 = st.columns([2, 1])
with col_t1:
    ticker_symbol = st.text_input(
        "Börsenkürzel / Ticker eingeben (z.B. RTO.L, OSPN, ALNY):",
        "RTO.L"
    ).upper().strip()
with col_t2:
    target_position_eur = st.number_input(
        "Zielgröße (€)",
        min_value=100,
        max_value=50000,
        value=1000,
        step=100,
        help="Der heilige Beate-Sandler-Geist: Zielgröße je Einzelposition!"
    )


# ============================================================
# HILFSFUNKTIONEN
# ============================================================

def safe_float(value, default=np.nan):
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def find_row(df, candidates):
    if df is None or df.empty:
        return None
    for candidate in candidates:
        for row in df.index:
            if candidate.lower() in str(row).lower():
                return row
    return None


def clean_series(series):
    if series is None:
        return pd.Series(dtype=float)
    try:
        s = pd.to_numeric(series, errors="coerce").dropna()
        if len(s) == 0:
            return pd.Series(dtype=float)
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
    s = clean_series(series)
    if len(s) < 4:
        return {"label": "⚪ Keine ausreichende Historie", "score": 60, "deltas": []}
    vals = s.values.astype(float)
    deltas = np.diff(vals)
    if vals[-1] < vals[-2]:
        label = "🔴 Rückläufig"
        score = 25
    else:
        delta_change = deltas[-1] - deltas[-2]
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
    return {"label": label, "score": score, "deltas": deltas.tolist()}


def growth_comparison(start, end):
    if pd.isna(start) or pd.isna(end) or start == 0:
        return np.nan
    return ((end / start) - 1) * 100


# ============================================================
# ENGINE
# ============================================================

if st.button("⚡ OmaKurz v2.2.2 starten"):
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info

        company_name = info.get("longName", ticker_symbol)
        sector = info.get("sector", "Unbekannt")
        current_price = safe_float(info.get("currentPrice", info.get("regularMarketPrice")))
        total_cash = safe_float(info.get("totalCash"), 0)
        total_debt = safe_float(info.get("totalDebt"), 0)
        net_cash = total_cash - total_debt

        rev_growth = safe_float(info.get("revenueGrowth"))
        profit_margin = safe_float(info.get("profitMargins"))
        if not pd.isna(rev_growth): rev_growth *= 100
        if not pd.isna(profit_margin): profit_margin *= 100

        try: financials = stock.financials
        except Exception: financials = pd.DataFrame()

        try: cashflow = stock.cashflow
        except Exception: cashflow = pd.DataFrame()

        try: balance_sheet = stock.balance_sheet
        except Exception: balance_sheet = pd.DataFrame()

        # ROWS & SERIES
        revenue_row = find_row(financials, ["Total Revenue", "Operating Revenue"])
        ocf_row = find_row(cashflow, ["Operating Cash Flow", "Total Cash From Operating Activities"])
        capex_row = find_row(cashflow, ["Capital Expenditure", "Purchase Of Property Plant And Equipment"])
        share_row = find_row(balance_sheet, ["Ordinary Shares Number", "Share Issued"])

        revenue_series = clean_series(financials.loc[revenue_row] if revenue_row is not None else None)
        ocf_series = clean_series(cashflow.loc[ocf_row] if ocf_row is not None else None)
        capex_series = clean_series(cashflow.loc[capex_row] if capex_row is not None else None)
        shares_series = clean_series(balance_sheet.loc[share_row] if share_row is not None else None)

        has_revenue = len(revenue_series) > 0
        has_ocf = len(ocf_series) > 0
        has_hist = len(revenue_series) >= 3
        has_shares = len(shares_series) >= 2
        has_capex = len(capex_series) > 0

        # EVIDENCE SCORE
        evidence_score = 30
        if has_revenue: evidence_score += 15
        if has_ocf: evidence_score += 15
        if has_hist: evidence_score += 15
        if has_shares: evidence_score += 10
        if has_capex: evidence_score += 5
        evidence_score = min(evidence_score, 100)

        st.markdown("### 🔍 Evidence & Datenabdeckung")
        e1, e2 = st.columns(2)
        with e1:
            st.write(f"• Umsatzdaten: {'🟢 Vorhanden' if has_revenue else '🔴 Fehlt'}")
            st.write(f"• Historie: {'🟢 3+ Jahre' if has_hist else '🟡 Begrenzt'}")
            st.write(f"• OCF: {'🟢 Vorhanden' if has_ocf else '🔴 Fehlt'}")
        with e2:
            st.write(f"• Aktienhistorie: {'🟢 Vorhanden' if has_shares else '🟡 Nicht ausreichend'}")
            st.write(f"• CapEx: {'🟢 Vorhanden' if has_capex else '🟡 Fehlt'}")
            st.write("• Pipeline & Primärquellen: ⚪ In v2.3")
        st.caption(f"Transparenz-/Datenabdeckungsindex: {evidence_score}/100")

        # FCF ENGINE
        fcf_series = pd.Series(dtype=float)
        if has_ocf and has_capex:
            try:
                combined = pd.concat([ocf_series.rename("OCF"), capex_series.rename("CapEx")], axis=1).dropna()
                if not combined.empty:
                    fcf_series = combined["OCF"] + combined["CapEx"]
            except Exception:
                pass

        # ACCELERATION
        acceleration = classify_acceleration(revenue_series)
        rev_accel_label = acceleration["label"]

        st.markdown("### ⚡ True Delta Acceleration")
        if len(revenue_series) >= 4:
            history_text = " → ".join(format_money(v / 1e9) for v in revenue_series.values)
            st.write(f"**Umsatz:** {history_text}")
            deltas = acceleration["deltas"]
            delta_text = " → ".join(format_money(v / 1e9) for v in deltas)
            st.write(f"**Jährliche Zuwächse:** {delta_text}")
            st.write(f"**Dynamik:** {rev_accel_label}")
        else:
            st.warning("Für eine belastbare Beschleunigungsanalyse liegen zu wenige historische Umsatzdaten vor.")

        # FCF DYNAMIK
        fcf_label = "⚪ Nicht ausreichend"
        fcf_current = fcf_series.iloc[-1] / 1e9 if len(fcf_series) > 0 else np.nan
        if len(fcf_series) >= 3:
            fcf_values = fcf_series.values
            if fcf_values[-1] < 0:
                fcf_label = "🟠 Cash Burn problematisch" if fcf_values[-2] >= fcf_values[-1] else "🟡 Cash Burn verbessert sich"
            else:
                fcf_label = "🟢 FCF verbessert sich" if fcf_values[-1] > fcf_values[-2] else "🟠 FCF verschlechtert sich"
        st.write(f"**FCF-Dynamik:** {fcf_label}")

        # CAPITAL & DILUTION DETECTIVE
        st.markdown("### 🕵️ Capital & Dilution Detective")
        share_change_pct = np.nan
        revenue_change_pct = np.nan

        if has_shares:
            s_start, s_end = shares_series.iloc[0], shares_series.iloc[-1]
            share_change_pct = growth_comparison(s_start, s_end)
            st.write(f"**Aktienzahl:** {s_start / 1e6:.1f} Mio. → {s_end / 1e6:.1f} Mio. ({share_change_pct:+.1f}%)")
        else:
            st.write("🟡 Keine ausreichende Aktienhistorie verfügbar.")

        if len(revenue_series) >= 2:
            revenue_change_pct = growth_comparison(revenue_series.iloc[0], revenue_series.iloc[-1])
            st.write(f"**Umsatz über denselben Zeitraum:** {revenue_change_pct:+.1f}%")

        if not pd.isna(share_change_pct):
            if share_change_pct > 10:
                dilution_delta_text = "🔴 Aktienzahl wächst deutlich schneller als der Umsatz." if (not pd.isna(revenue_change_pct) and revenue_change_pct < share_change_pct) else "🟡 Aktienzahl stark gestiegen – Gegenleistung prüfen."
            elif share_change_pct > 3:
                dilution_delta_text = "🟡 Aktienzahl moderat gestiegen – Ursache prüfen."
            else:
                dilution_delta_text = "🟢 Aktienzahl relativ stabil."
        else:
            dilution_delta_text = "⚪ Keine ausreichende Aktienhistorie."
        st.write(f"**Dilution Delta:** {dilution_delta_text}")

        # FINANCING DETECTIVE
        st.markdown("### 💰 Finanzierungs-Detektiv")
        op_cashflow_current = ocf_series.iloc[-1] / 1e9 if len(ocf_series) > 0 else np.nan
        runway_years = np.nan
        if not pd.isna(fcf_current) and fcf_current < 0 and total_cash > 0:
            runway_years = total_cash / (abs(fcf_current) * 1e9)

        st.write(f"• **Cash:** {format_money(total_cash / 1e9)}")
        st.write(f"• **Debt:** {format_money(total_debt / 1e9)}")
        st.write(f"• **Netto-Cash:** {format_money(net_cash / 1e9)}")

        if not pd.isna(runway_years):
            if runway_years < 2: st.error(f"🚨 Rechnerische Cash-Runway nur ca. {runway_years:.1f} Jahre.")
            elif runway_years < 4: st.warning(f"🟡 Rechnerische Cash-Runway ca. {runway_years:.1f} Jahre.")
            else: st.success(f"🟢 Rechnerische Cash-Runway ca. {runway_years:.1f} Jahre.")

        # ====================================================
        # 👑 OMA-KERN-URTEIL & BEATE-SANDLER-GEIST (1000€ ZIEL)
        # ====================================================
        st.markdown("### 🧓 OmaKurz-Kern-Urteil & Beate-Sandler-Ziel")

        oma_category = "🛠️ Muss noch geschliffen werden"
        oma_color = "warning"

        is_profitable = not pd.isna(profit_margin) and profit_margin > 10
        is_fcf_strong = not pd.isna(fcf_current) and fcf_current > 0.1
        is_high_growth = not pd.isna(rev_growth) and rev_growth > 15

        if is_profitable and is_fcf_strong:
            oma_category = "👑 Kronjuwel (Starke Cash-Maschine & Margen)"
            oma_color = "success"
        elif is_high_growth and (pd.isna(profit_margin) or profit_margin < 15):
            oma_category = "💎 Rohdiamant (Hohes Wachstum, wird operativ geschliffen)"
            oma_color = "info"
        elif net_cash > 0 and not is_profitable:
            oma_category = "🪙 Solides Polster, sucht noch den Durchbruch"
            oma_color = "info"

        if oma_color == "success":
            st.success(f"**Status:** {oma_category}")
        elif oma_color == "info":
            st.info(f"**Status:** {oma_category}")
        else:
            st.warning(f"**Status:** {oma_category}")

        # Beate-Sandler-Geist Berechnung
        if not pd.isna(current_price) and current_price > 0:
            shares_needed = target_position_eur / current_price
            st.metric(
                label=f"🎯 Beate-Sandler-Ziel ({target_position_eur:,.0f} €)",
                value=f"{shares_needed:.1f} Aktien",
                delta=f"Aktueller Kurs: {current_price:.2f} €"
            )
            st.caption(
                f"Der Geist von Beate Sandler: Um die Zielposition von {target_position_eur:,.0f} € "
                f"voll aufzubauen, werden bei {current_price:.2f} € genau {shares_needed:.1f} Anteile benötigt."
            )
        else:
            st.warning("Aktueller Kurs konnte für die Zielpositions-Berechnung nicht ermittelt werden.")

        st.markdown(f"💬 *„Schön, mein Junge. Bei **{company_name}** stehen die Zeichen auf Klarheit. Disziplin schlägt Jede Hype!“*")

    except Exception as e:
        st.error(f"Fehler bei der v2.2.2 Execution: {e}")
        
