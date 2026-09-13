import streamlit as st
import yfinance as ticker_data

st.set_page_config(page_title="OmaKurz™ Scanner v1.7 Pro", page_icon="🧭", layout="centered")

st.title("🧭 OMAKURZ™ SCANNER v1.7")
st.caption("Evidence Engine Pro Edition — Gewichtete Scores & Beschleunigungs-Forensik")

ticker_symbol = st.text_input("Börsenkürzel / Ticker eingeben (z.B. OSPN, ALNY, RTO.L):", "OSPN").upper()

if st.button("⚡ Pro-Forensik-Analyse starten"):
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

        # Historische Wachstumsprüfung für Beschleunigungs-Logik holen
        hist = stock.history(period="3y")
        # Vereinfachte Annäherung für den Trend aus Quartals-/Jahresdaten
        acceleration_status = "📊 Solide / Stabil"
        if len(hist) > 200:
            # Check Kurs- oder Trend-Momentum als Indikator
            recent_return = (hist['Close'].iloc[-1] - hist['Close'].iloc[-50]) / hist['Close'].iloc[-50]
            older_return = (hist['Close'].iloc[-50] - hist['Close'].iloc[-100]) / hist['Close'].iloc[-100]
            if recent_return > older_return and rev_growth > 10:
                acceleration_status = "⚡ Beschleunigung aktiv (Dynamik steigt)"
            elif recent_return < older_return:
                acceleration_status = "🛑 Dynamik bricht ab / Verlangsamung"

        st.header(f"Ergebnisse für {company_name} ({sector})")

        # -------------------------------------------------------------
        # 1. ENTGELTETES EVIDENCE- & DATEN-VERTRAUEN (Getrennt von Schulden)
        # -------------------------------------------------------------
        evidence_points = 0
        if info.get("totalRevenue") is not None: evidence_points += 25
        if info.get("operatingCashflow") is not None: evidence_points += 25
        if info.get("sharesOutstanding") is not None: evidence_points += 25
        if pe_ratio is not None or pb_ratio is not None: evidence_points += 25

        st.info(f"🛡️ **OmaKurz™ Evidence Schild:** Marktkapitalisierung: {market_cap:.2f} Mrd. USD | EV: {enterprise_val:.2f} Mrd. USD | **Daten-Transparenz: {evidence_points}/100**")

        # -------------------------------------------------------------
        # 2. VETO & STATUS LOGIK
        # -------------------------------------------------------------
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

        # -------------------------------------------------------------
        # 3. GEWICHTETER OMA-SCORE & KURZ-SCORE
        # -------------------------------------------------------------
        # Oma-Score (Gewichtet nach Netto-Cash, OCF, Schuldenfreiheit)
        oma_substanz = 20
        if net_cash > 0: oma_substanz += 35
        elif net_cash > -2: oma_substanz += 15
        if op_cashflow > 0.5: oma_substanz += 35
        elif op_cashflow > 0: oma_substanz += 20
        oma_substanz = min(oma_substanz, 100)

        # Kurz-Score (Gewichtet nach Wachstum & Marge)
        kurz_zukunft = 20
        if rev_growth > 15: kurz_zukunft += 45
        elif rev_growth > 5: kurz_zukunft += 25
        if profit_margin > 15: kurz_zukunft += 35
        elif profit_margin > 0: kurz_zukunft += 15
        kurz_zukunft = min(kurz_zukunft, 100)

        # 🧠 OMAKURZ-KERN-URTEIL (Inkl. Ray's Klassiker)
        st.markdown("### 🧓 OmaKurz-Kern-Urteil")
        if oma_substanz >= 75 and kurz_zukunft >= 60:
            st.markdown("💬 *„Die Story ist groß – aber diesmal liegt tatsächlich einiges auf dem Tisch.“*")
        elif kurz_zukunft >= 70 and oma_substanz < 50:
            st.markdown("💬 *„Hier bezahlt der Markt nicht nur für das heutige Unternehmen, sondern bereits für einen beträchtlichen Teil der Zukunft.“*")
        else:
            st.markdown("💬 *„Schöne Geschichte, mein Junge. Jetzt zeig mir erstmal, was wirklich auf the Tisch liegt.“*")

        # METRIK-BLOCKS
        st.markdown("---")
        col_a, col_b, col_c = st.columns(3)
        with col_a: st.metric("🏛️ Oma - Substanz", f"{oma_substanz} / 100")
        with col_b: st.metric("🚀 Kurz - Zukunft", f"{kurz_zukunft} / 100")
        with col_c: st.metric("⚡ Dynamic / Growth", f"{rev_growth:.1f} % p.a.")

        st.write(f"**Beschleunigungs-Status:** {acceleration_status}")

        # -------------------------------------------------------------
        # 4. FINANZIERUNGS-DETEKTIV & SUBSTANZ
        # -------------------------------------------------------------
        st.subheader("🕵️ 1. Finanzierungs-Detektiv & Substanz")
        st.write(f"**Netto-Cash:** {net_cash:.2f} Mrd. USD " + ("(🟢 Positiv)" if net_cash > 0 else "(🔴 Negativ)"))
        st.write(f"**Operativer Cashflow:** {op_cashflow:.2f} Mrd. USD")
        st.write(f"**Finanzierung:** {'✅ Solide aus Betrieb' if op_cashflow > 0 else '⚠️ Externer Kapitalbedarf möglich'}")

        # -------------------------------------------------------------
        # 5. BEATE SANDER HYPOTHETISCHES RECHENBEISPIEL
        # -------------------------------------------------------------
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

        st.caption("OmaKurz™ Scanner v1.7 Pro • Anti-FOMO Analyse-System")

    except Exception as e:
        st.error(f"Fehler bei der Pro-Forensik-Analyse: {e}")
        
