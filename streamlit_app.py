import streamlit as st
import yfinance as ticker_data
import numpy as np

# Page Config
st.set_page_config(page_title="OmaKurz™ Scanner v1.5 Forensik", page_icon="🧭", layout="centered")

st.title("🧭 OMAKURZ™ SCANNER v1.5")
st.caption("Forensik Edition — Anti-FOMO & Beate-Sander-Strategie")

# Ticker Input
ticker_symbol = st.text_input("Börsenkürzel / Ticker eingeben (z.B. OSPN, ALNY, RTO.L):", "OSPN").upper()

if st.button("⚡ Forensik-Analyse starten"):
    try:
        stock = ticker_data.Ticker(ticker_symbol)
        info = stock.info
        
        # Data Extraction
        company_name = info.get("longName", ticker_symbol)
        pe_ratio = info.get("trailingPE", None)
        rev_growth = info.get("revenueGrowth", 0) * 100 if info.get("revenueGrowth") else 0
        profit_margin = info.get("profitMargins", 0) * 100 if info.get("profitMargins") else 0
        current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
        op_cashflow = info.get("operatingCashflow", 0)
        total_debt = info.get("totalDebt", 0)
        total_cash = info.get("totalCash", 0)
        net_cash = total_cash - total_debt
        shares_outstanding = info.get("sharesOutstanding", 1)

        st.header(f"Ergebnisse für {company_name}")

        # 1. FORENSIK: ACCELERATION SCORE (Ray's Feature)
        # Bsp-Logik für Dynamik-Beschleunigung aus historischen Daten
        hist_acceleration_score = "Stabil"
        if rev_growth > 20:
            hist_acceleration_score = "🚀 Hohe Beschleunigung"
        elif rev_growth > 5:
            hist_acceleration_score = "📈 Solides Basis-Wachstum"
        else:
            hist_acceleration_score = "⚠️ Träge / Stagnierend"

        # 2. VETO-SYSTEM & DIAMANT-KLASSIFIZIERUNG (Hardened Diamond Logic)
        has_veto = False
        veto_reasons = []

        if net_cash < 0 and op_cashflow <= 0:
            has_veto = True
            veto_reasons.append("Negativer Cashflow bei zeitgleicher Verschuldung")
        
        if pe_ratio and pe_ratio > 80:
            has_veto = True
            veto_reasons.append("Extrem überhöhte Bewertung (KGV > 80)")

        # Status Bestimmung
        if not has_veto and op_cashflow > 0 and (pe_ratio and pe_ratio < 25):
            status = "💎 Kronjuwel / Geschliffener Diamant"
            status_color = "success"
        elif not has_veto and rev_growth > 15:
            status = "💠 Rohdiamant mit Wachstumspotenzial"
            status_color = "info"
        else:
            status = "⚠️ Spekulativ / Substanz-Prüfung erforderlich"
            status_color = "warning"

        # Display Status
        if status_color == "success":
            st.success(f"**STATUS:** {status}")
        elif status_color == "info":
            st.info(f"**STATUS:** {status}")
        else:
            st.warning(f"**STATUS:** {status}")

        if has_veto:
            st.error(f"⛔ **Veto-Sperre aktiv:** Kein Kronjuwel-Status möglich wegen: {', '.join(veto_reasons)}")

        # 3. NIKOLA / THERANOS STRESSTEST-WARNUNG
        if op_cashflow <= 0 and rev_growth > 30:
            st.error("🚨 **STRESSTEST-ALARM (Nikola/Theranos-Muster):** Hohes narratives Wachstum bei negativem operativen Cashflow! Hohes Risiko von Kapitalverwässerung.")

        # 4. FAIR-VALUE-KORRIDOR (Ray's Feature)
        st.subheader("⚖️ Fair-Value-Korridor")
        if pe_ratio:
            fair_low = current_price * (15 / pe_ratio) if pe_ratio > 0 else current_price * 0.7
            fair_high = current_price * (22 / pe_ratio) if pe_ratio > 0 else current_price * 1.1
            st.write(f"• **Aktueller Kurs:** {current_price:.2f} USD (KGV: {pe_ratio:.1f})")
            st.write(f"• **OmaKurz Korridor:** {min(fair_low, fair_high):.2f} USD – {max(fair_low, fair_high):.2f} USD")
        else:
            st.write("Keine KGV-Basis für Korridor vorhanden.")

        # 5. TARGET 1.000 € BEATE SANDER INTEGRATION (Burhan's Feature)
        st.markdown("---")
        st.subheader("🎯 Beate Sander 1.000 € Zielmarken-Rechner")
        
        ziel_summe = 1000.0
        # Rechnerische Stückzahl
        stueckzahl = ziel_summe / current_price if current_price > 0 else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Tranchen-Strategie:**")
            if "Kronjuwel" in status:
                st.write("• **Start-Tranche:** 500 € (50% Direkt-Einstieg)")
                st.write("• **Rest:** 2 Tranchen à 250 € bei Rücksetzern")
            else:
                st.write("• **Start-Tranche:** 250 € (25% Ansparen)")
                st.write("• **Rest:** 3 Tranchen à 250 € nach Meilensteinen")
            st.write(f"• **Ziel-Anzahl:** ca. **{stueckzahl:.2f} Aktien**")

        with col2:
            st.markdown("**50 € Sparplan-Dauer:**")
            sparrate = 50.0
            monate = ziel_summe / sparrate
            st.write(f"• **Laufzeit:** {monate:.0f} Monate ({monate/12:.1f} Jahre)")
            st.write("• **Effekt:** Optimaler Cost-Average-Effekt")

        st.caption("OmaKurz™ Scanner v1.5 Forensik • Keine Anlageberatung")

    except Exception as e:
        st.error(f"Fehler bei der Forensik-Analyse: {e}")
            
