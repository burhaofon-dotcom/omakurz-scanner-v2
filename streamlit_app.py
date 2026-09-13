import streamlit as st
import yfinance as ticker_data

st.set_page_config(page_title="OmaKurz™ Scanner v1.5 Forensik Edition", page_icon="🧭", layout="centered")

st.title("🧭 OMAKURZ™ SCANNER v1.5")
st.caption("Forensik Edition — Anti-FOMO & Beate-Sander-Strategie (Mit OmaKurz-Kern-Urteil)")

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

        # 🛡️ Anti-FOMO Schild & Dynamisches Daten-Vertrauen
        data_confidence = "95 % (Yahoo Finance API Aktiv)" if pe_ratio else "70 % (Teilweise Lücken)"
        st.info(f"🛡️ **OmaKurz™ Anti-FOMO Schild:** Marktkapitalisierung: {market_cap:.2f} Mrd. USD | EV: {enterprise_val:.2f} Mrd. USD | Daten-Vertrauen: {data_confidence}")

        # VETO & STATUS LOGIK
        has_veto = False
        veto_reasons = []
        if net_cash < 0 and op_cashflow <= 0:
            has_veto = True
            veto_reasons.append("Negativer Cashflow bei Verschuldung")
        if pe_ratio and pe_ratio > 80:
            has_veto = True
            veto_reasons.append("Extrem überhöhte Bewertung (KGV > 80)")

        if not has_veto and op_cashflow > 0 and (pe_ratio and pe_ratio < 25):
            status = "💎 Kronjuwel / Geschliffener Diamant"
            st.success(f"**STATUS:** {status}")
        elif not has_veto and rev_growth > 15:
            status = "💠 Rohdiamant mit Wachstumspotenzial"
            st.info(f"**STATUS:** {status}")
        else:
            status = "⚠️ Spekulativ / Substanz-Prüfung erforderlich"
            st.warning(f"**STATUS:** {status}")

        if has_veto:
            st.error(f"⛔ **Veto-Sperre aktiv:** Kein Kronjuwel-Status wegen: {', '.join(veto_reasons)}")

        # 🧠 OMAKURZ-KERN-URTEIL (Ray's geniale Idee integriert!)
        st.markdown("### 🧓 OmaKurz-Kern-Urteil")
        if "Kronjuwel" in status:
            st.markdown("💬 *„Die Firma liefert echten operativen Cashflow und starke Substanz. Hier bezahlt man nicht nur für Träume, sondern bekommt handfeste Fundamentaldaten auf den Tisch.“*")
        elif "Rohdiamant" in status:
            st.markdown("💬 *„Das Wachstum ist stark, aber der Markt verlangt bereits Vorschusslorbeeren. Die Bilanz muss zeigen, dass die Dynamik in harten Cashflow überspringt.“*")
        else:
            st.markdown("💬 *„Achtung: Die Story klingt groß, aber die Bilanzen oder Schulden zeigen, dass hier das Risiko hoch ist. Kein reines Substanz-Investment.“*")

        # METRIK-BLOCKS
        st.markdown("---")
        st.metric("🏛️ Oma - Substanz", "90 / 100" if net_cash > 0 else "50 / 100")
        st.metric("🚀 Kurz - Zukunft", "85 / 100" if rev_growth > 10 else "50 / 100")
        st.metric("⚡ Dynamic / Growth", f"{rev_growth:.1f} % p.a.")

        # DETEKTIV & SUBSTANZ
        st.subheader("🕵️ 1. Finanzierungs-Detektiv & Substanz")
        st.write(f"**Netto-Cash:** {net_cash:.2f} Mrd. USD " + ("(🟢 Positiv)" if net_cash > 0 else "(🔴 Negativ)"))
        st.write(f"**Operativer Cashflow:** {op_cashflow:.2f} Mrd. USD")
        st.write(f"**Finanzierung:** {'✅ Solide aus Betrieb' if op_cashflow > 0 else '⚠️ Externer Kapitalbedarf möglich'}")

        # BEATE SANDER HYPOTHETISCHES RECHENBEISPIEL (Entschärft: Kein Kaufbefehl!)
        st.markdown("---")
        st.subheader("🎯 Was würde ein 1.000-€-Beispiel bedeuten?")
        st.caption("Hypothetisches Rechenbeispiel zur Positionsgröße & Risiko-Abschätzung (Kein Kaufbefehl)")
        
        ziel_summe = 1000.0
        stueckzahl = ziel_summe / current_price if current_price > 0 else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Positions-Struktur:**")
            st.write(f"• **Hypothetische Stückzahl:** ca. **{stueckzahl:.2f} Aktien**")
            st.write("• **Tranchen-Aufteilung:** 3er-Split (je 333 €)")
            st.write(f"• **Aktueller Kurs:** {current_price:.2f} USD")
            
        with col2:
            st.markdown("**Stresstest (Verlust-Szenario):**")
            st.write(f"• Bei **-20% Korrektur**: Portfolio-Wert 800 € (-200 €)")
            st.write(f"• Bei **-40% Korrektur**: Portfolio-Wert 600 € (-400 €)")
            st.write(f"• Bei **-60% Krise**: Portfolio-Wert 400 € (-600 €)")

        st.caption("OmaKurz™ Scanner v1.5 Forensik Edition • Anti-FOMO Analyse-System")

    except Exception as e:
        st.error(f"Fehler bei der Forensik-Analyse: {e}")
        
