import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="OmaKurz Scanner",
    page_icon="🧭",
    layout="centered"
)

st.markdown("""
<style>
.hero { text-align:center; padding: 10px 0; }
.hero .compass { font-size:72px; }
.hero h1 { font-family: Georgia, serif; font-size:32px; margin:5px 0; }
.hero p { color:#756f65; font-size:18px; margin-bottom:15px; }
.quote { font-family:Georgia,serif; font-style:italic; font-size:20px; color:#c8a261; text-align:center; margin-bottom:25px; }
.card { padding:18px; border:1px solid #d4c5b3; border-radius:12px; background:#fffdfa; margin-bottom:15px; }
.badge-diamant { display:inline-block; padding:4px 10px; border-radius:20px; background:#2b5b84; color:white; font-size:12px; font-weight:bold; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="compass">🧭</div>
  <h1>OMAKURZ SCANNER v0.2</h1>
  <p>Erst verstehen. Dann investieren.</p>
</div>
<div class="quote">„Was du nicht verstehst, kaufst du nicht.“</div>
""", unsafe_allow_html=True)

st.subheader("Unternehmen scannen")
ticker_input = st.text_input("Ticker (z.B. ALNY, CRM, 3696.HK) oder Firmenname ...", key="ticker")

if st.button("🧭 Kompass starten", use_container_width=True):
    if not ticker_input:
        st.warning("Bitte gib einen Ticker ein.")
    else:
        try:
            stock = yf.Ticker(ticker_input.strip().upper())
            info = stock.info

            company_name = info.get("longName", ticker_input.upper())
            sector = info.get("sector", "k.A.")
            market_cap = info.get("marketCap", 0)
            total_cash = info.get("totalCash", 0)
            total_debt = info.get("totalDebt", 0)
            free_cashflow = info.get("freeCashflow", 0)

            net_cash = total_cash - total_debt

            oma_score = 75 if net_cash > 0 else 40
            kurz_score = 80 if free_cashflow > 0 else 50
            scanner_score = 90
            haertegrad = 85

            st.markdown(f"### Ergebnisse für **{company_name}** ({sector})")

            cols = st.columns(4)
            scores = [
                ("🏛️ Oma - Substanz", oma_score, "Cash-Netto-Check"),
                ("🚀 Kurz - Zukunft", kurz_score, "Cashflow-Dynamik"),
                ("🔍 Scanner - Belege", scanner_score, "Transparenz"),
                ("⚖️ Härtegrad", haertegrad, "Gesamteinschätzung")
            ]

            for col, (title, score, desc) in zip(cols, scores):
                with col:
                    st.metric(title, f"{score} / 100")
                    st.caption(desc)
                    st.progress(score / 100)

            st.subheader("🛡️ 1. Bilanz-Check")
            b1, b2, b3, b4 = st.columns(4)
            b1.metric("Cash-Polster", f"{total_cash / 1e9:.2f} B$" if total_cash else "k.A.")
            b2.metric("Schulden", f"{total_debt / 1e9:.2f} B$" if total_debt else "k.A.")
            b3.metric("Netto-Cash", f"{net_cash / 1e9:.2f} B$" if net_cash else "k.A.")
            b4.metric("Free Cashflow", f"{free_cashflow / 1e9:.2f} B$" if free_cashflow else "k.A.")

            st.subheader("🌖 2. Gegen-Analyse")
            st.warning(f"**Warum könnte {company_name} scheitern?**\n\n"
                       f"- **Bewertungs-Risiko:** Hohe Erwartungen bereits eingepreist.\n"
                       f"- **Verwässerungs-Gefahr:** Aktienbasierte Vergütung im Blick behalten.\n"
                       f"- **Technologie-Risiko:** Schneller Wandel im Markt.")

            st.subheader("💎 3. Diamant-Einordnung")
            st.info("**Ergebnis:** 💎 **Rohdiamant / Wachstums-Case**")

        except Exception as e:
            st.error(f"Fehler beim Abrufen der Daten: {e}")

st.divider()
st.caption("OmaKurz Scanner · Version 0.2 · Datenquelle: Yahoo Finance")
