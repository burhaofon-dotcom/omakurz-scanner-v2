# ==========================================
# OmaKurz™ Kompass ULTRA GLOBAL
# Mit weltweitem Ticker-Support, EUR-Umrechnung,
# Live-Währungen, News-Check & Gemini-KI
# ==========================================

import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai

# Seiten-Konfiguration
st.set_page_config(
    page_title="Oma-Kurz-Kompass ULTRA",
    page_icon="🌌",
    layout="wide"
)

# --- SESSION STATE INITIALISIEREN ---
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []

# --- SIDEBAR: API-KEY & WATCHLIST ---
st.sidebar.title("🧠 KI-Gehirn aktivieren")
api_key_input = st.sidebar.text_input("Gemini API-Key eingeben:", type="password")
st.sidebar.markdown("*Dein Schlüssel aus Google AI Studio.*")
st.sidebar.markdown("---")

st.sidebar.title("📌 Ultra Global Watchlist")
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
st.title("🌌 Oma-Kurz-Kompass ULTRA")
st.markdown("""
*Das ultimative, globale Analyse-Terminal. Scannt Aktien weltweit (Europa, US, Asien, Emerging Markets wie Türkei, Brasilien), 
rechnet alles in Euro um und durchleuchtet Bilanzen, Schulden sowie das aktuelle Marktgeschehen.*
""")
st.markdown("---")

col_input1, col_input2 = st.columns([3, 1])
with col_input1:
    ticker_input = st.text_input("Ticker-Symbol eingeben (z.B. THYAO.IS, 7203.T, T, ENB, RWE.DE):", value="THYAO.IS").strip().upper()
with col_input2:
    st.write("") 
    st.write("")
    analysis_triggered = st.button("🚀 ULTRA Stresstest starten", use_container_width=True)

if analysis_triggered and ticker_input:
    if not api_key_input:
        st.error("🚨 Bitte gib links in der Seitenleiste deinen Gemini API-Key ein!")
    else:
        with st.spinner(f"Führe weltweite Analyse & Marktdaten-Check für {ticker_input} durch...") :
            try:
                # 1. Daten von Yahoo Finance holen
                stock = yf.Ticker(ticker_input)
                info = stock.info
                
                name = info.get('longName', ticker_input)
                price = info.get('currentPrice', info.get('regularMarketPrice', info.get('previousClose', 0.0)))
                currency = info.get('currency', 'USD')

                sector = info.get('sector', 'Unbekannt (Global/Emerging)')
                industry = info.get('industry', 'Unbekannt')
                pe_ratio = info.get('trailingPE', "N/A")
                market_cap = info.get('marketCap', 0)
                profit_margins = info.get('profitMargins', 0.0)
                
                # HARTE BILANZDATEN
                debt_to_equity = info.get('debtToEquity', "N/A") 
                payout_ratio = info.get('payoutRatio', 0.0)      
                
                # 2. WÄHRUNGSRECHNUNG IN EURO (EUR)
                price_in_eur = price
                
                if currency != 'EUR' and price > 0:
                    try:
                        fx_ticker_str = f"{currency}EUR=X"
                        fx_data = yf.Ticker(fx_ticker_str).info
                        fx_rate = fx_data.get('regularMarketPrice', fx_data.get('previousClose', None))
                        
                        if not fx_rate or fx_rate == 0:
                            fx_inv = yf.Ticker(f"EUR{currency}=X").info
                            inv_rate = fx_inv.get('regularMarketPrice', fx_inv.get('previousClose', 0))
                            if inv_rate > 0:
                                fx_rate = 1.0 / inv_rate
                                
                        if fx_rate and fx_rate > 0:
                            price_in_eur = price * fx_rate
                        else:
                            # Sichere Fallbacks falls Yahoo-Forex blockiert
                            if currency == 'USD': price_in_eur = price * 0.92
                            elif currency == 'GBP': price_in_eur = price * 1.18
                            elif currency == 'TRY': price_in_eur = price * 0.027
                            elif currency == 'JPY': price_in_eur = price * 0.006
                            elif currency == 'HKD': price_in_eur = price * 0.12
                            elif currency == 'BRL': price_in_eur = price * 0.17
                    except:
                        pass 

                # 3. KI-Gehirn konfigurieren (gemini-3.6-flash)
                genai.configure(api_key=api_key_input)
                model = genai.GenerativeModel('gemini-3.6-flash')
                
                # 4. Der ULTRA Prompt mit Bilanz-Stresstest, Währungsrisiko & News-Stimmung
                prompt = f"""
                Du bist der 'Oma-Kurz-Kompass ULTRA' - ein weltweit agierender, kompromissloser Finanzanalyst nach Beate Sander (Substanz & Schulden max. 25-50%) und Ray Kurzweil (Zukunfts-Accelerator).
                Führe einen umfassenden Ultra-Stresstest für das Unternehmen {name} (Ticker: {ticker_input}) aus.
                
                GLOBALES MARKTDATEN-PROFIL:
                - Landeswährung: {currency} | Kurs vor Ort: {price}
                - Berechneter Kurs in EURO (€): {price_in_eur:.2f} EUR
                - Branche / Sektor: {sector} / {industry}
                - KGV: {pe_ratio}
                - Gewinnmarge: {profit_margins * 100 if profit_margins else 'N/A'} %
                - Schuldenquote (Debt-to-Equity): {debt_to_equity} % (Über 25% ist ein massives Warnsignal!)
                - Ausschüttungsquote (Payout Ratio): {payout_ratio * 100 if payout_ratio else 'N/A'} %
                
                DEINE AUFGABE:
                1. Bewerte das Unternehmen unbestechlich nach harten Bilanzen, Verschuldung und Substanz.
                2. Beziehe länderspezifische Risiken (z.B. Inflations- und Währungsturbulenzen in Emerging Markets wie Türkei, Brasilien oder globale Lieferketten-Risiken) in die Bewertung ein.
                3. Nutze dein aktuelles Wissen über die jüngsten Markttrends, Quartalszahlen oder makroökonomischen Nachrichten zu diesem Unternehmen für eine aktuelle Stimmungs-Einordnung.
                
                Gib das Ergebnis EXAKT in dieser Struktur aus (formatiert mit Markdown):
                
                ### 💎 Härtegrad: [Wähle eines: Unpolierter Rohstein / Dividenden-Falle / Solider Wert / Geschliffener Brillant]
                
                **Globaler Bilanz- & Schulden-Stresstest:**
                [Deine knallharte Analyse zur Verschuldung, Substanz und Währungsstabilität in 2-3 Sätzen]
                
                **Der Zukunfts-Accelerator & Marktsituation:**
                [Deine Analyse zur technologischen Skalierung, Wettbewerbsfähigkeit und aktuellen News-Tendenz]
                
                **Dynamischer ULTRA KI-Score:** [Vergib eine Punktzahl von 0 bis 100. Werte mit schweren Schulden oder hohen Emerging-Market-Risiken max. 50 Punkte] / 100
                """
                
                # KI-Antwort generieren
                response = model.generate_content(prompt)
                ai_analysis = response.text
                
                # 5. Ergebnisse anzeigen
                st.markdown("---")
                st.subheader(f"Ergebnis für: {name} ({ticker_input})")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Kurs (in EUR)", f"{price_in_eur:.2f} EUR", f"Orig: {price:.2f} {currency}")
                with col2:
                    st.metric("KGV", f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else "N/A")
                with col3:
                    st.metric("Schuldenquote (D/E)", f"{debt_to_equity}%" if isinstance(debt_to_equity, (int, float)) else "N/A")
                with col4:
                    st.metric("Payout Ratio", f"{payout_ratio*100:.1f}%" if isinstance(payout_ratio, (int, float)) else "N/A")
                    
                st.markdown("---")
                st.info(f"🌌 ULTRA Modus aktiv | Währung umgerechnet in EUR | Modell: gemini-3.6-flash")
                
                # KI-Ausgabe einblenden
                st.markdown(ai_analysis)
                
                # Watchlist-Button
                if st.button("📌 Zur ULTRA Watchlist hinzufügen"):
                    watch_label = f"{name} ({ticker_input}) - {price_in_eur:.2f} EUR"
                    if watch_label not in st.session_state.watchlist:
                        st.session_state.watchlist.append(watch_label)
                        st.success("Erfolgreich zur Watchlist hinzugefügt!")
                        st.rerun()
                    else:
                        st.warning("Bereits auf der Watchlist.")
                        
            except Exception as e:
                st.error(f"Fehler bei der ULTRA-Analyse von {ticker_input}: {e}")

# --- BRANDING FOOTER ---
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray; font-size: 0.85em;'>"
    "Engineered by Gemini & Burhao (ULTRA Global Edition) &nbsp;|&nbsp; Data powered by Yahoo Finance"
    "</p>", 
    unsafe_allow_html=True
)
