import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="OmaKurz Scanner v0.4",
    page_icon="🧭",
    layout="centered"
)

# Styling
st.markdown("""
<style>
.hero { text-align:center; padding: 10px 0; }
.hero .compass { font-size:72px; }
.hero h1 { font-family: Georgia, serif; font-size:32px; margin:5px 0; }
.hero p { color:#756f65; font-size:18px; margin-bottom:15px; }
.quote { font-family:Georgia,serif; font-style:italic; font-size:18px; color:#c8a261; text-align:center; margin-bottom:25px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="compass">🧭</div>
  <h1>OMAKURZ SCANNER v0.4</h1>
  <p>Erst verstehen. Dann investieren.</p>
</div>
<div class="quote">„Was du nicht verstehst, kaufst du nicht.“</div>
""", unsafe_allow_html=True)

st.subheader("Unternehmen scannen")
ticker_input = st.text_input("Ticker (z.B. 6501.T, AAPL, ALNY, NVDA) eingeben ...", key="ticker")

if st.button("🧭 Kompass starten", use_container_width=True):
    if not ticker_input:
        st.warning("Bitte gib ein gültiges Ticker-Symbol ein.")
    else:
        try:
            stock = yf.Ticker(ticker_input.strip().upper())
            info = stock.info

            # Basisdaten
            company_name = info.get("longName", ticker_input.upper())
            sector = info.get("sector", "Unbekannt")
            currency = info.get("currency", "USD")
            
            # 1. Substanz & Schulden
            total_cash = info.get("totalCash", 0) or 0
            total_debt = info.get("totalDebt", 0) or 0
            net_cash = total_cash - total_debt
            pe_ratio = info.get("trailingPE", None) or info.get("forwardPE", None)
            pb_ratio = info.get("priceToBook", None)

            # 2. Cashflow, Marge & Cash-Burn
            op_cashflow = info.get("operatingCashflow", 0) or 0
            free_cashflow = info.get("freeCashflow", None)
            profit_margin = (info.get("profitMargins", 0) or 0) * 100

            # 3. Dividende
            div_yield = (info.get("dividendYield", 0) or 0) * 100
            payout_ratio = (info.get("payoutRatio", 0) or 0) * 100

            # 4. Investoren & Anker-Aktionäre
            inst_ownership = (info.get("heldPercentInstitutions", 0) or 0) * 100
            insider_ownership = (info.get("heldPercentInsiders", 0) or 0) * 100

            # 5. Zukunft & Wachstum
            rev_growth = (info.get("revenueGrowth", 0) or 0) * 100

            # --- SCORES BERECHNEN ---
            
            # Oma - Substanz (Max 100)
            oma_score = 50
            if net_cash > 0: oma_score += 20
            else: oma_score -= 15
            
            # Strikte Bestrafung bei negativem Cashflow (Cash-Burn)
            if op_cashflow < 0:
                oma_score -= 20 # Verbrennt laufend Geld!
                
            if pb_ratio and pb_ratio < 3.0: oma_score += 15
            if payout_ratio > 0 and payout_ratio <= 70: oma_score += 15
            elif payout_ratio > 90: oma_score -= 25 # Substanzfraß
            
            oma_score = max(10, min(100, oma_score))

            # Kurz - Zukunft (Max 100)
            kurz_score = 50
            if rev_growth > 5: kurz_score += 20
            if profit_margin > 10: kurz_score += 15
            if inst_ownership > 40: kurz_score += 15
            kurz_score = max(10, min(100, kurz_score))

            # Scanner - Transparenz
            scanner_score = 95 if pe_ratio and pb_ratio else 70

            # Härtegrad
            haertegrad = int((oma_score * 0.45) + (kurz_score * 0.35) + (scanner_score * 0.20))

            # --- AUSGABE ---
            st.markdown(f"### Ergebnisse für **{company_name}** ({sector})")
            
            # 4 Säulen
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("🏛️ Oma - Substanz", f"{oma_score} / 100")
            c2.metric("🚀 Kurz - Zukunft", f"{kurz_score} / 100")
            c3.metric("🔍 Scanner - Belege", f"{scanner_score} / 100")
            c4.metric("⚖️ Härtegrad", f"{haertegrad} / 100")

            st.divider()

            # 1. Bilanz & Kennzahlen
            st.subheader("🛡️ 1. Substanz & Finanzierung")
            b1, b2, b3, b4 = st.columns(4)
            b1.metric("Netto-Cash", f"{net_cash / 1e9:.2f} Mrd. {currency}")
            b2.metric("Gesamtschulden", f"{total_debt / 1e9:.2f} Mrd. {currency}")
            b3.metric("KBV (Substanz)", f"{pb_ratio:.2f}" if pb_ratio else "k.A.")
            b4.metric("Gewinnmarge", f"{profit_margin:.1f} %")

            # 2. Cashflow & Finanzierungs-Quelle
            st.subheader("💸 2. Cashflow & Geld-Quelle")
            f1, f2, f3 = st.columns(3)
            f1.metric("Operativer Cashflow", f"{op_cashflow / 1e9:.2f} Mrd. {currency}")
            f2.metric("KGV", f"{pe_ratio:.1f}" if pe_ratio else "k.A.")
            
            # Status der Geld-Quelle
            if op_cashflow > 0:
                f3.metric("Finanzierungs-Quelle", "✅ Aus Betrieb")
            else:
                f3.metric("Finanzierungs-Quelle", "🚨 Fremdgeld / Burn")

            # 3. Anker-Investoren & Dividende
            st.subheader("👑 3. Anker-Investoren & Dividende")
            d1, d2, d3, d4 = st.columns(4)
            d1.metric("Dividendenrendite", f"{div_yield:.2f} %")
            d2.metric("Ausschüttungsquote", f"{payout_ratio:.1f} %")
            d3.metric("Profi-Investoren", f"{inst_ownership:.1f} %")
            d4.metric("Insider / Gründer", f"{insider_ownership:.1f} %")

            # 4. Dynamische Gegen-Analyse (Risikocheck inkl. Wandelanleihen)
            st.subheader("🌖 4. Gegen-Analyse (Risikocheck)")
            risks = []
            
            if op_cashflow < 0:
                risks.append("🚨 **Cash-Burn & Finanzierungs-Druck:** Das Unternehmen verbrennt operativ Geld! Hohe Gefahr von **Wandelanleihen, neuen Schulden oder Aktienverwässerung**.")
            if total_debt > total_cash and total_cash > 0:
                risks.append("⚠️ **Refinanzierungs-Risiko:** Schulden übersteigen das Cash-Polster. Abhängigkeit von Banken oder Anleihemärkten.")
            if pe_ratio and pe_ratio > 35:
                risks.append("⚠️ **Hohes Bewertungs-Risiko:** Sehr hohes KGV – enttäuschte Erwartungen können den Kurs stark belasten.")
            if payout_ratio > 85:
                risks.append("⚠️ **Substanzfraß bei Dividende:** Die Dividende wird kaum oder gar nicht durch den Cashflow gedeckt.")

            if not risks:
                st.success("✅ Keine akuten Warnsignale in der automatischen Gegen-Analyse gefunden!")
            else:
                for r in risks:
                    st.warning(r)

            # 5. OmaKurz Fazit
            st.subheader("💎 5. OmaKurz™ Fazit")
            if op_cashflow < 0:
                st.error("⚡ **Hochspekulativer Case (Cash-Burn):** Vorsicht! Die Finanzierung läuft nicht aus dem eigenen Geschäft. Prüfe Laufzeiten von Anleihen/Wandelanleihen genau!")
            elif oma_score >= 70 and kurz_score >= 70:
                st.info("💎 **A-Diamant / Qualitäts-Festung:** Hohe Substanz & verlässlicher Cash-Zufluss.")
            elif oma_score >= 60:
                st.info("🏛️ **Substanz-Anker:** Solide Bilanz, gut geschützt für ruhige Phasen.")
            else:
                st.warning("⚠️ **Durchschnittlicher Case:** Eingeschränkte Substanz oder hohe Bewertung.")

        except Exception as e:
            st.error(f"Fehler beim Abrufen der Daten: {e}")

st.divider()
st.caption("OmaKurz Scanner · Version 0.4 · Live-Datenquelle: Yahoo Finance")
            
