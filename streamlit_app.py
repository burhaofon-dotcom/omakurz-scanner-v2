import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="OmaKurz™ Scanner v2.2.8",
    page_icon="🧭",
    layout="centered"
)

st.title("🧭 OMAKURZ™ Scanner v2.2.8")
st.caption(
    "Financing Detective • Dilution Delta • Global FX & Scale Engine • "
    "Material-Hierarchie & Beate-Sandler-Whitepaper"
)

col_t1, col_t2 = st.columns([2, 1])
with col_t1:
    ticker_symbol = st.text_input(
        "Börsenkürzel / Ticker eingeben (z.B. 7203.T, 0005.HK, ALNY, RTO.L):",
        "7203.T"
    ).upper().strip()
with col_t2:
    target_position_eur = st.number_input(
        "Zielgröße (€)",
        min_value=100,
        max_value=50000,
        value=1000,
        step=100,
        help="Der heilige Beate-Sandler-Geist: Zielgröße je Einzelposition in Euro!"
    )


# ============================================================
# HILFSFUNKTIONEN & GLOBALE FX & SKALIERUNGS-ENGINE
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


@st.cache_data(ttl=3600)
def get_global_fx_rate(from_currency):
    curr = from_currency.upper().strip()
    if curr == "GBX":
        return 0.01 * get_global_fx_rate("GBP")
    if curr in ["EUR", ""]:
        return 1.0
    
    pair = f"{curr}EUR=X"
    try:
        fx_ticker = yf.Ticker(pair)
        fx_info = fx_ticker.info
        rate = fx_info.get("currentPrice", fx_info.get("regularMarketPrice"))
        if rate and not pd.isna(rate) and rate > 0:
            return float(rate)
    except Exception:
        pass
    
    fallbacks = {
        "USD": 0.92,
        "GBP": 1.17,
        "JPY": 0.0061,
        "HKD": 0.118,
        "SGD": 0.69,
        "CHF": 1.07,
        "CAD": 0.68,
        "AUD": 0.61
    }
    return fallbacks.get(curr, 1.0)


def format_financials_in_eur(value_in_native, fx_rate):
    if pd.isna(value_in_native):
        return "n/a"
    val_eur = value_in_native * fx_rate
    val_mrd_eur = val_eur / 1e9
    
    abs_val = abs(val_mrd_eur)
    if abs_val >= 1:
        return f"{val_mrd_eur:.2f} Mrd. €"
    elif abs_val >= 0.001:
        return f"{val_mrd_eur * 1000:.0f} Mio. €"
    else:
        return f"{val_eur:.2f} €"


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

if st.button("⚡ OmaKurz v2.2.8 starten"):
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info

        company_name = info.get("longName", ticker_symbol)
        sector = info.get("sector", "Unbekannt")
        
        currency = info.get("currency", "USD")
        raw_price = safe_float(info.get("currentPrice", info.get("regularMarketPrice")))

        if currency == "GBX":
            price_in_native = raw_price / 100.0 if not pd.isna(raw_price) else np.nan
            fx_rate = get_global_fx_rate("GBP")
        else:
            price_in_native = raw_price
            fx_rate = get_global_fx_rate(currency)

        price_in_eur = price_in_native * fx_rate if not pd.isna(price_in_native) else np.nan

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

        evidence_score = 30
        if has_revenue: evidence_score += 15
        if has_ocf: evidence_score += 15
        if has_hist: evidence_score += 15
        if has_shares: evidence_score += 10
        if has_capex: evidence_score += 5
        evidence_score = min(evidence_score, 100)

        # 👑 HIER IST DER FIRMENNAME WIEDER SAUBER PLAZIERT!
        st.markdown(f"## 🏢 {company_name}")
        st.caption(f"Ticker: {ticker_symbol} | Sektor: {sector} | Heimatwährung: {currency}")

        st.markdown("### 🔍 Evidence & Datenabdeckung")
        e1, e2 = st.columns(2)
        with e1:
            st.write(f"• Umsatzdaten: {'🟢 Vorhanden' if has_revenue else '🔴 Fehlt'}")
            st.write(f"• Historie: {'🟢 3+ Jahre' if has_hist else '🟡 Begrenzt'}")
            st.write(f"• OCF: {'🟢 Vorhanden' if has_ocf else '🔴 Fehlt'}")
        with e2:
            st.write(f"• Aktienhistorie: {'🟢 Vorhanden' if has_shares else '🟡 Nicht ausreichend'}")
            st.write(f"• CapEx: {'🟢 Vorhanden' if has_capex else '🟡 Fehlt'}")
            st.write("• Whitepaper-Ready: 🟢 Aktiv")
        st.caption(f"Transparenz-/Datenabdeckungsindex: {evidence_score}/100")

        fcf_series = pd.Series(dtype=float)
        if has_ocf and has_capex:
            try:
                combined = pd.concat([ocf_series.rename("OCF"), capex_series.rename("CapEx")], axis=1).dropna()
                if not combined.empty:
                    fcf_series = combined["OCF"] + combined["CapEx"]
            except Exception:
                pass

        acceleration = classify_acceleration(revenue_series)
        rev_accel_label = acceleration["label"]

        st.markdown("### ⚡ True Delta Acceleration (in Mrd. €)")
        if len(revenue_series) >= 4:
            history_text = " → ".join(format_financials_in_eur(v, fx_rate) for v in revenue_series.values)
            st.write(f"**Umsatz:** {history_text}")
            deltas = acceleration["deltas"]
            delta_text = " → ".join(format_financials_in_eur(v, fx_rate) for v in deltas)
            st.write(f"**Jährliche Zuwächse:** {delta_text}")
            st.write(f"**Dynamik:** {rev_accel_label}")
        else:
            st.warning("For eine belastbare Beschleunigungsanalyse liegen zu wenige historische Umsatzdaten vor.")

        fcf_label = "⚪ Nicht ausreichend"
        fcf_current = fcf_series.iloc[-1] / 1e9 if len(fcf_series) > 0 else np.nan
        if len(fcf_series) >= 3:
            fcf_values = fcf_series.values
            if fcf_values[-1] < 0:
                fcf_label = "🟠 Cash Burn problematisch" if fcf_values[-2] >= fcf_values[-1] else "🟡 Cash Burn verbessert sich"
            else:
                fcf_label = "🟢 FCF verbessert sich" if fcf_values[-1] > fcf_values[-2] else "🟠 FCF verschlechtert sich"
        st.write(f"**FCF-Dynamik:** {fcf_label}")

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

        st.markdown("### 💰 Finanzierungs-Detektiv (in Mrd. €)")
        runway_years = np.nan
        if not pd.isna(fcf_current) and fcf_current < 0 and total_cash > 0:
            runway_years = total_cash / (abs(fcf_current) * 1e9)

        st.write(f"• **Cash:** {format_financials_in_eur(total_cash, fx_rate)}")
        st.write(f"• **Debt:** {format_financials_in_eur(total_debt, fx_rate)}")
        st.write(f"• **Netto-Cash:** {format_financials_in_eur(net_cash, fx_rate)}")

        if not pd.isna(runway_years):
            if runway_years < 2: st.error(f"🚨 Rechnerische Cash-Runway nur ca. {runway_years:.1f} Jahre.")
            elif runway_years < 4: st.warning(f"🟡 Rechnerische Cash-Runway ca. {runway_years:.1f} Jahre.")
            else: st.success(f"🟢 Rechnerische Cash-Runway ca. {runway_years:.1f} Jahre.")

        # ====================================================
        # 👑 OMA-KERN-URTEIL & MATERIAL-HIERARCHIE (WHITEPAPER)
        # ====================================================
        st.markdown("### 🧓 OmaKurz-Kern-Urteil & Material-Hierarchie")

        is_profitable = not pd.isna(profit_margin) and profit_margin > 8
        is_fcf_strong = not pd.isna(fcf_current) and fcf_current > 0.05
        is_high_growth = not pd.isna(rev_growth) and rev_growth > 10

        if is_profitable and is_fcf_strong:
            oma_category = "👑 Kronjuwel / Diamant-Klasse (Starke Cash-Maschine & Margen)"
            oma_color = "success"
        elif is_profitable or (net_cash > 0 and is_high_growth):
            oma_category = "🛡️ Platin-Anker (Solide, wertbeständige Substanz für die Ewigkeit)"
            oma_color = "success"
        elif is_high_growth:
            oma_category = "⚡ Kupfer-Schmiede (Wachstumswert, im operativen Aufbau)"
            oma_color = "info"
        else:
            oma_category = "🪨 Rohstein / Ungehobelter Findling (Muss im Prozess noch geschliffen werden)"
            oma_color = "warning"

        if oma_color == "success":
            st.success(f"**Status:** {oma_category}")
        elif oma_color == "info":
            st.info(f"**Status:** {oma_category}")
        else:
            st.warning(f"**Status:** {oma_category}")

        # Beate-Sandler-Ziel
        if not pd.isna(price_in_eur) and price_in_eur > 0:
            shares_needed = target_position_eur / price_in_eur
            st.metric(
                label=f"🎯 Beate-Sandler-Ziel ({target_position_eur:,.0f} €)",
                value=f"{shares_needed:.1f} Aktien",
                delta=f"Kurs: {price_in_native:,.2f} {currency} (≈ {price_in_eur:.2f} €)"
            )
            st.caption(
                f"Der Geist von Beate Sandler: Um die Zielposition von {target_position_eur:,.0f} € "
                f"aufzubauen, werden bei einem Kurs von {price_in_eur:.2f} € "
                f"({price_in_native:,.2f} {currency}) genau {shares_needed:.1f} Anteile benötigt."
            )
        else:
            st.warning("Aktueller Kurs oder globaler Wechselkurs konnte nicht ermittelt werden.")

        # Whitepaper-Erklärungsbox für die Familie
        with st.expander("📖 Whitepaper-Glossar für den Familienrat (Klick zum Öffnen)"):
            st.markdown("""
            **Wie liest man den OmaKurz™ Report?**
            * **👑 Kronjuwel / Diamant:** Die absolute Königsklasse – sprudelt massig Free Cash Flow und hohe Margen. Sofort kaufbereit.
            * **🛡️ Platin-Anker:** Felsenfest, krisensicher und verlässlich. Unser stabiler Rückhalt im Portfolio.
            * **⚡ Kupfer-Schmiede:** Dynamisch, leitet Energie und wächst stark, wird im operativen Prozess weiter veredelt.
            * **🪨 Rohstein (Findling):** Rohmaterial. Zeigt Potenzial, muss aber noch geschliffen werden (höhere Aufmerksamkeit nötig).
            * **🎯 Beate-Sandler-Ziel:** Gibt exakt vor, wie viele Anteile wir brauchen, um unsere feste Zielgröße (€) zu erreichen – ganz unabhängig von der Landeswährung!
            """)

        st.markdown(f"💬 *„Jetzt steht der Name wieder dick und fett oben, mein Junge! So weiß jeder im Familienrat sofort, welches Schwergewicht gerade analysiert wird.“*")

    except Exception as e:
        st.error(f"Fehler bei der v2.2.8 Execution: {e}")
        
