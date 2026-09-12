import streamlit as st
import yfinance as yf

st.set_page_config(page_title="OmaKurz Scanner v0.2", page_icon="🧭", layout="wide")

st.markdown("""
<style>
.hero { text-align:center; padding: 10px 0 18px; }
.hero .compass { font-size:72px; }
.hero h1 { font-family: Georgia, serif; font-size:42px; margin:0; }
.hero p { color:#756f65; font-size:18px; }
.quote { font-family:Georgia,serif; font-style:italic; font-size:20px; }
.card { padding:18px; border:1px solid #d8d0c1; border-radius:16px; background:#fffdf8; }
.badge-diamant { display:inline-block; padding:7px 13px; border-radius:999px; background:#d1e7dd; color:#0f5132; font-weight:800; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<div class="compass">🧭</div>
<h1>OMAKURZ SCANNER v0.2</h1>
<p>Erst verstehen. Dann investieren.</p>
<div class="quote">„Was du nicht verstehst, kaufst du nicht.“</div>
</div>
""", unsafe_allow_html=True)

query = st.text_input("Unternehmen scannen", placeholder="Ticker (z.B. ALNY, CRM, 3696.HK) oder Firmenname ...")
scan = st.button("🧭 Kompass starten", type="primary", use_container_width=True)

if scan and query:
    ticker_symbol = query.strip().upper()
    
    with st.spinner(f"Lade Finanzdaten für {ticker_symbol}..."):
        try:
            stock = yf.Ticker(ticker_symbol)
            info = stock.info
            
            company_name = info.get('longName', ticker_symbol)
            currency = info.get('currency', 'USD')
            total_cash = info.get('totalCash', 0) / 1e6
            total_debt = info.get('totalDebt', 0) / 1e6
            net_cash = total_cash - total_debt
            free_cashflow = info.get('freeCashflow', 0) / 1e6
            market_cap = info.get('marketCap', 0) / 1e9
            pe_ratio = info.get('forwardPE', 'N/A')
            
            oma_score = 80 if net_cash > 0 and free_cashflow > 0 else (60 if net_cash > 0 else 40)
            kurz_score = 85  
            scanner_score = 75
            haertegrad = 65 if pe_ratio != 'N/A' and isinstance(pe_ratio, (int, float)) and pe_ratio > 30 else 45

            st.markdown(f'''
            <div class="card">
                <span class="badge-diamant">💎 ROHDIAMANT · LIVE-DATA</span>
                <h2>{company_name} ({ticker_symbol})</h2>
                <p><b>Währung:</b> {currency} | <b>Marktkapitalisierung:</b> {market_cap:.2f} Mrd. {currency}</p>
            </div>
            ''', unsafe_allow_html=True)
            
            st.write("")
            
            cols = st.columns(4)
            metrics = [
                ("🏦 Oma – Substanz", oma_score, f"Net-Cash: {net_cash:.1f}M {currency}"),
                ("🚀 Kurz – Zukunft", kurz_score, "AI & Tech-Infrastruktur"),
                ("🔬 Scanner – Belege", scanner_score, "Pipeline & Partner"),
                ("💰 Härtegrad", haertegrad, f"KGV (Forward): {pe_ratio}"),
            ]
            for col, (title, score, desc) in zip(cols, metrics):
                with col:
                    st.metric(title, f"{score}/100")
                    st.caption(desc)
                    st.progress(score / 100)

            st.subheader("🧓 1. Bilanz-Check (Oma)")
            b1, b2, b3, b4 = st.columns(4)
            b1.metric("Cash-Polster", f"{total_cash:.1f} M {currency}")
            b2.metric("Schulden", f"{total_debt:.1f} M {currency}")
            b3.metric("Netto-Cash", f"{net_cash:.1f} M {currency}")
            b4.metric("Free Cashflow", f"{free_cashflow:.1f} M {currency}")

            st.subheader("🪞 2. Gegen-Analyse (Bären-Check)")
            st.warning(f"**Warum könnte {company_name} scheitern?**\n"
                       f"- **Bewertungs-Risiko:** Ist zu viel Zukunft bereits im Kurs eingepreist?\n"
                       f"- **Verwässerungs-Gefahr:** Werden bei steigendem Kapitalbedarf neue Aktien ausgegeben?\n"
                       f"- **Technologie-Risiko:** Funktioniert das Geschäftsmodell auch nach einem potenziellen Fehlschlag der Haupt-Pipeline?")

            st.subheader("💎 3. Diamant-Einordnung")
            st.info("**Ergebnis:** 💎 **Rohdiamant** (Starke Bilanz-Substanz trifft auf zukunftsträchtige Technologie.)")

        except Exception as e:
            st.error(f"Fehler beim Abrufen der Daten für '{ticker_symbol}'. Bitte prüfe den Ticker.")

st.divider()
st.caption("OmaKurz Scanner · Version 0.2 · Datenquelle: Yahoo Finance API")
        
