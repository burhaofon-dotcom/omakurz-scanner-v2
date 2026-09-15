# ==========================================
# OmaKurz™ Kompass PRO - Hauptanwendung
# Mit Gemini-KI, Stresstest & Härtegrad-Analyse
# ==========================================

import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai

# Seiten-Konfiguration
st.set_page_config(
    page_title="Oma-Kurz-Kompass PRO",
    page_icon="💎",
    layout="wide"
)

# --- SESSION STATE INITIALISIEREN ---
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []

# --- SIDEBAR: API-KEY & WATCHLIST ---
st.sidebar.title("🧠 KI-Gehirn aktivieren")
api_key_input = st.sidebar.text_input("Gemini API-Key eingeben (für den Pro-Modus):", type="password")
st.sidebar.markdown("*Dein kostenloser Schlüssel aus Google AI Studio.*")
st.sidebar.markdown("---")

st.sidebar.title("📌 Deine Watchlist")
if st.session_state.watchlist:
    for i, item in enumerate(st.session_state.watchlist):
        col_w1, col_w2 = st.sidebar.columns([4, 1])
        with col_w1:
            st.write(f"• {item}")
        with col_w2:
            if st.button("❌", key=f"del_{i}"):
                st.session_state.watchlist.pop(i)
                st.rerun()
    if st.sidebar.button("🗑️ Watchlist leeren"):
        st.session_state.watchlist = []
        st.rerun()
else:
    st.sidebar.info("Noch keine Werte gespeichert.")

# --- HAUPTSEITE ---
st.title("💎 Oma-Kurz-Kompass PRO")
st.markdown("""
*Der ultimative, KI-gestützte Anlage-Kompass. Sucht gnadenlos nach dem Zukunfts-Accelerator 
und bestraft Schuldenberge und Dividenden-Fallen.*
""")
st.markdown("---")

col_input1, col_input2 = st.columns([3, 1])
with col_input1:
    ticker_input = st.text_input("Ticker-Symbol eingeben (z.B. ENB, T, RKT.L, NEE):", value="T").upper()
with col_input2:
    st.write("") 
    st.write("")
    analysis_triggered = st.button("🚀 KI-Stresstest starten", use_container_width=True)

if analysis_triggered and ticker_input:
    if not api_key_input:
        st.error("🚨 Bitte gib links in der Seitenleiste deinen Gemini API-Key ein, um den Stresstest zu starten!")
    else:
        with st.spinner(f"Analysiere Bilanz & Fundamentaldaten für {ticker_input}...") :
            try:
                # 1. Daten von Yahoo Finance holen
                stock = yf.Ticker(ticker_input)
                info = stock.info
                
                name = info.get('longName', ticker_input)
                price = info.get('currentPrice', info.get('regularMarketPrice', 0.0))
                currency = info.get('currency', 'USD')
                
                # Pence zu GBP Korrektur
                if currency == 'GBp':
                    price = price / 100.0
                    currency = 'GBP'

                sector = info.get('sector', 'Unbekannt')
                industry = info.get('industry', 'Unbekannt')
                pe_ratio = info.get('trailingPE', "N/A")
                market_cap = info.get('marketCap', 0)
                profit_margins = info.get('profitMargins', 0.0)
                
                # HARTE BILANZDATEN FÜR DEN STRESSTEST
                debt_to_equity = info.get('debtToEquity', "N/A") # Über 25-50% wird kritisch!
                payout_ratio = info.get('payoutRatio', 0.0)      # Wie viel vom Gewinn geht für Dividende drauf?
                
                # 2. KI-Gehirn konfigurieren
                genai.configure(api_key=api_key_input)
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                
                # 3. Der knallharte Prompt für die KI
                prompt = f"""
                Du bist der 'Oma-Kurz-Kompass' - ein gnadenloser Finanzanalyst nach der Philosophie von Beate Sander (Substanz) und Ray Kurzweil (exponentielles Wachstum).
                Führe einen Stresstest für das Unternehmen {name} (Ticker: {ticker_input}) aus.
                
                HIER SIND DIE NACKTEN ZAHLEN:
                - Branche: {sector} / {industry}
                - KGV: {pe_ratio}
                - Gewinnmarge: {profit_margins * 100 if profit_margins else 'N/A'} %
                - Schuldenquote (Debt-to-Equity): {debt_to_equity} % (Über 25% ist ein massives Warnsignal!)
                - Ausschüttungsquote (Payout Ratio): {payout_ratio * 100 if payout_ratio else 'N/A'} %
                
                DEINE AUFGABE:
                Bewerte das Unternehmen schonungslos. Beantworte diese Punkte im direkten Klartext:
                1. Gibt es ein Schuldenproblem? (Bestrafe alles über 25% extrem hart!)
                2. Ist die Dividende eine Falle, die Wachstum und Innovation abwürgt?
                3. Hat das Unternehmen einen "Accelerator" (einen Zukunfts-Turbo zur Skalierung) oder lebt es nur im Niemandsland der Vergangenheit?
                
                Gib das Ergebnis EXAKT in dieser Struktur aus (formatiert mit Markdown):
                
                ### 💎 Härtegrad: [Wähle eines: Unpolierter Rohstein / Dividenden-Falle / Solider Wert / Geschliffener Brillant]
                
                **Der Stresstest (Bilanz & Schulden):**
                [Deine knallharte Analyse zu den Schulden und der Dividenden-Ausschüttung in 2-3 Sätzen]
                
                **Der Zukunfts-Accelerator:**
                [Deine Analyse zum exponentiellen Wachstum: Gibt es Innovation oder nur Stillstand?]
                
                **Dynamischer KI-Score:** [Vergib eine Punktzahl von 0 bis 100. Werte mit massiven Schulden und ohne Accelerator dürfen MAXIMAL 55 Punkte bekommen!] / 100
                """
                
                # KI-Antwort generieren
                response = model.generate_content(prompt)
                ai_analysis = response.text
                
                # 4. Ergebnisse anzeigen
                st.markdown("---")
                st.subheader(f"Ergebnis für: {name} ({ticker_input})")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Kurs", f"{price:.2f} {currency}")
                with col2:
                    st.metric("KGV", f"{pe_ratio:.2f}" if isinstance(pe_ratio, float) else "N/A")
                with col3:
                    st.metric("Schuldenquote (D/E)", f"{debt_to_equity}%" if isinstance(debt_to_equity, float) else "N/A")
                with col4:
                    st.metric("Payout Ratio", f"{payout_ratio*100:.1f}%" if isinstance(payout_ratio, float) else "N/A")
                    
                st.markdown("---")
                
                # KI-Ausgabe direkt einblenden
                st.markdown(ai_analysis)
                
                # Watchlist-Button
                if st.button("📌 Zur Watchlist hinzufügen"):
                    watch_label = f"{name} ({ticker_input}) - Stresstest absolviert"
                    if watch_label not in st.session_state.watchlist:
                        st.session_state.watchlist.append(watch_label)
                        st.success("Erfolgreich zur Watchlist hinzugefügt! (Siehe Sidebar links)")
                        st.rerun()
                    else:
                        st.warning("Bereits auf der Watchlist.")
                        
            except Exception as e:
                st.error(f"Fehler bei der Analyse von {ticker_input}: {e}")

# --- BRANDING FOOTER ---
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray; font-size: 0.85em;'>"
    "Engineered by Gemini & Burhao  |  Data powered by Yahoo Finance"
    "</p>", 
    unsafe_allow_html=True
)
