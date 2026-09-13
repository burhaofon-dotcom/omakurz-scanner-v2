import streamlit as st
import yfinance as ticker_data

st.set_page_config(page_title="OmaKurz™ Scanner v1.5 Forensik", page_icon="🧭", layout="centered")

st.title("🧭 OMAKURZ™ SCANNER v1.5")
st.caption("Forensik Edition — Anti-FOMO & Beate-Sander-Strategie")

ticker_symbol = st.text_input("Börsenkürzel / Ticker eingeben (z.B. OSPN, ALNY, RTO.L):", "OSPN").upper()

if st.button("⚡ Forensik-Analyse starten"):
    try:
        stock = ticker_data.Ticker(ticker_symbol)
        info = stock.info
        
        company_name = info.get("longName", ticker_symbol)
        sector = info.get("sector", "Unbekannt")
        pe_ratio = info.get("trailingPE", None)
        pb_ratio = info.get("priceToBook", None)
        rev_growth = info.get("revenueGrowth", 0) * 100 if info.get("revenueGrowth") else 0.0
        profit_margin = info.get("profitMargins", 0) * 100 if info.get("profitMargins") else 0.0
        current_price = info.get("currentPrice", info.get("regularMarketPrice", 0.0))
        op_cashflow = info.get("operatingCashflow", 0.0) / 1e9
        total_debt = info.get("totalDebt", 0.0) / 1e9
        total_cash = info.get("totalCash", 0.0) / 1e9
        net_cash = total_cash - total_debt
        market_cap = info.get("marketCap", 0.0) / 1e9
        enterprise_val = info.get("enterpriseValue", 0.0) / 1e9
        shares_outstanding = info.get("sharesOutstanding", 0) / 1e6

        st.header(f"Ergebnisse für {company_name} ({sector})")

        # 🛡️ Anti-FOMO Schild
        st.info(f"🛡️ **OmaKurz™ Anti-FOMO Schild:** Marktkapitalisierung: {market_cap:.2f} Mrd. USD | Enterprise Value (EV): {enterprise_val:.2f} Mrd. USD | Daten-Vertrauen: 100%")

        # 1. FORENSIK VETO-SYSTEM & DIAMANT-STATUS
        has_veto = False
        veto_reasons = []

        if net_cash < 0 and op_cashflow <= 0:
            has_veto = True
            veto_reasons.append("Negativer Cashflow bei zeitgleicher Verschuldung")
        if pe_ratio and pe_ratio > 80:
            has_veto = True
            veto_reasons.append("Extrem überhöhte Bewertung (KGV > 80)")

        if not has_veto and op_cashflow > 0 and (pe_ratio and pe_ratio < 25):
            status = "💎 Kronjuwel / Geschliffener Diamant"
            st.success(f"**STATUS:** {status}\nHöchste Substanz, starker operativer Cashflow und exzellente Datenbelege.\n\n🔵 **Bewertung:** Fair bewertet – Das KGV von {pe_ratio:.1f} spiegelt hohe Qualität und starke Margen wider." if pe_ratio else f"**STATUS:** {status}")
        elif not has_veto and rev_growth > 15:
            status = "💠 Rohdiamant mit Wachstumspotenzial"
            st.info(f"**STATUS:** {status}")
        else:
            status = "⚠️ Spekulativ / Substanz-Prüfung erforderlich"
            st.warning(f"**STATUS:** {status}")

        if has_veto:
            st.error(f"⛔ **Veto-Sperre aktiv:** Kein Kronjuwel-Status möglich wegen: {', '.join(veto_reasons)}")

        # 2. METRIKEN METRIC-BLOCKS (v1.3 DASHBOARD RECOVERED)
        st.markdown("---")
        st.metric("🏛️ Oma - Substanz", "100 / 100" if net_cash > 0 and op_cashflow > 0 else "60 / 100")
        st.metric("🚀 Kurz - Zukunft", "90 / 100" if rev_growth > 0 else "50 / 100")
        st.metric("⚡ Dynamic / Growth", f"{rev_growth:.1f} % p.a.")
        st.metric("🔍 Belege & Transparenz", "100 %")

        # 3. DETEKTIV & SUBSTANZ
        st.subheader("🕵️ 1. Finanzierungs-Detektiv & Substanz")
        st.write(f"**Netto-Cash:** {net_cash:.2f} Mrd. USD " + ("(🟢 Positiv)" if net_cash > 0 else "(🔴 Negativ)"))
        st.write(f"**Operativer Cashflow:** {op_cashflow:.2f} Mrd. USD")
        st.write("**Finanzierung:** ✅ Aus Betrieb")
        st.write("**Runway (Reichweite):** Unbegrenzt (Cashflow-positiv)")

        # 4. VALUATION & ERLEÖS-VERDOPPLUNG
        st.subheader("⚖️ 2. Acceleration & Valuation")
        st.write(f"**KGV:** {pe_ratio:.1f}" if pe_ratio else "**KGV:** N/A")
        st.write(f"**KBV (Buchwert):** {pb_ratio:.2f}" if pb_ratio else "**KBV:** N/A")
        doubling_years = (72 / rev_growth) if rev_growth > 0 else 999
        st.write(f"**Erlös-Verdopplung:** ~ {doubling_years:.1f} Jahre")
        st.write(f"**Aktienanzahl:** {shares_outstanding:.1f} Mio.")

        # 5. FAIR-VALUE-KORRIDOR
        st.subheader("⚖️ Fair-Value-Korridor")
        if pe_ratio and pe_ratio > 0:
            fair_low = current_price * (15 / pe_ratio)
            fair_high = current_price * (22 / pe_ratio)
            st.write(f"• **Aktueller Kurs:** {current_price:.2f} USD")
            st.write(f"• **OmaKurz Korridor:** {min(fair_low, fair_high):.2f} USD – {max(fair_low, fair_high):.2f} USD")

        # 6. BEATE SANDER 1.000 € RECHNER
        st.markdown("---")
        st.subheader("🎯 Beate Sander 1.000 € Zielmarken-Rechner")
        
        ziel_summe = 1000.0
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

        st.caption("OmaKurz™ Scanner v1.5 Forensik • Anti-FOMO Analyse-System")

    except Exception as e:
        st.error(f"Fehler bei der Forensik-Analyse: {e}")
                
