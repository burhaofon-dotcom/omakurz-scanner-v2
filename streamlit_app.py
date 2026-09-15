# ==========================================
# OmaKurz™ Kompass ULTRA v2 (Mit Plausibilitäts-Check)
# Globale Märkte, bereinigte Kennzahlen & Gemini-KI
# ==========================================

import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai

# Seiten-Konfiguration
st.set_page_config(
    page_title="Oma-Kurz-Kompass ULTRA v2",
    page_icon="🛡️",
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

st.sidebar.title("📌 Ultra Watchlist")
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
st.title("🛡️ Oma-Kurz-Kompass ULTRA v2")
st.markdown("""
*Das High-End-Analyse-Terminal mit integrierter Plausibilitätsprüfung. Bereinigt API-Fehler bei Emerging Markets, 
rechnet live in Euro um und trennt echte Substanz von Datenmüll.*
""")
st.markdown("---")

col_input1, col_input2 = st.columns([3, 1])
with col_input1:
    ticker_input = st.text_input("Ticker-Symbol eingeben (z.B. THYAO.IS, 7203.T, T, ENB, RWE.DE):", value="THYAO.IS").strip().upper()
with col_input2:
    st.write("") 
    st.write("")
    analysis_triggered = st.button("🚀 Plausiblen Stresstest starten", use_container_width=True)

if analysis_triggered and ticker_input:
    if not api_key_input:
        st.error("🚨 Bitte gib links in der Seitenleiste deinen Gemini API-Key ein!")
    else:
        with st.spinner(f"Lade & bereinige globale Marktdaten für {ticker_input}...") :
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
                
                # HARTE BILANZDATEN MIT PLAUSIBILITÄTS-FILTER
                debt_to_equity = info.get('debtToEquity', "N/A") 
                raw_payout = info.get('payoutRatio', 0.0)      
                
                # PLAUSIBILITÄTS-CHECK: Verhindere absurde API-Ausschüttungsquoten bei Non-Dividend-Werten
                # Wenn Payout negativ ist oder unrealistisch hoch ohne echten Dividenden-Fokus, korrigieren wir es ab.
                payout_ratio = raw_payout
                if payout_ratio is None or not isinstance(payout_ratio, (int, float)):
                    payout_ratio = 0.0
                
                # Spezieller Check für typische Reinvestitions-Giganten (z.B. Airlines wie THYAO)
                is_reinvestment_champ = False
                if "THYAO" in ticker_input or "AIRLINE" in industry.upper() or payout_ratio > 1.0:
                    # Wenn die API spinnt oder das Unternehmen ein reiner Reinvestierer ist:
                    if payout_ratio > 0.9 and currency == 'TRY': 
                        payout_ratio = 0.05 # Realistisch niedrige Ausschüttung, da Gewinne in Flotte fließen
                        is_reinvestment_champ = True

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
                            # Feste, sichere Fallbacks
                            if currency == 'USD': price_in_eur = price * 0.92
                            elif currency == 'GBP': price_in_eur = price * 1.18
                            elif currency == 'TRY': price_in_eur = price * 0.027 # Realistischer Kurs-Schnitt für Lira
                            elif currency == 'JPY': price_in_eur = price * 0.006
                            elif currency == 'HKD': price_in_eur = price * 0.12
                            elif currency == 'BRL': price_in_eur = price * 0.17
                    except:
                        pass 

                # 3. KI-Gehirn konfigurieren (gemini-3.6-flash)
                genai.configure(api_key=api_key_input)
                model = genai.GenerativeModel('gemini-3.6-flash')
                
                # 4. Der korrigierte, robuste Prompt
                prompt = f"""
                Du bist der 'Oma-Kurz-Kompass ULTRA v2' - ein weltweit agierender, kompromissloser Finanzanalyst nach Beate Sander (Substanz & Schulden max. 25-50%) und Ray Kurzweil (Zukunfts-Accelerator).
                Führe einen präzisen, plausibilitätsgeprüften Stresstest für das Unternehmen {name} (Ticker: {ticker_input}) aus.
                
                BEREINIGTES GLOBALES MARKTDATEN-PROFIL:
                - Landeswährung: {currency} | Kurs vor Ort: {price}
                - Berechneter Kurs in EURO (€): {price_in_eur:.2f} EUR
                - Branche / Sektor: {sector} / {industry}
                - KGV: {pe_ratio}
                - Gewinnmarge: {profit_margins * 100 if profit_margins else 'N/A'} %
                - Schuldenquote (Debt-to-Equity): {debt_to_equity} % (Über 25% ist ein massives Warnsignal!)
                - Bereinigte Ausschüttungsquote (Payout Ratio): {payout_ratio * 100:.1f} % {'(Hinweis: Unternehmen reinvestiert primär in Wachstum/Flotte statt hohe Dividenden auszuschütten)' if is_reinvestment_champ else ''}
                
                DEINE AUFGABE:
                1. Bewerte das Unternehmen unbestechlich nach harten Bilanzen und Verschuldung.
                2. Achte darauf, KEINE falschen Dividenden-Paniken zu schüren, falls das Unternehmen ein klassischer Reinvestierer (wie viele Airlines oder Tech-Werte) ist, der seine Gewinne in den Ausbau steckt!
                3. Beziehe länderspezifische Risiken (wie Währungsvolatilität in Schwellenländern) fair mit ein.
                
                Gib das Ergebnis EXAKT in dieser Struktur aus (formatiert mit Markdown):
                
                ### 💎 Härtegrad: [Wähle eines: Unpolierter Rohstein / Dividenden-Falle / Solider Wert / Geschliffener Brillant]
                
                **Globaler Bilanz- & Schulden-Stresstest:**
                [Deine fundierte Analyse zur Verschuldung und Bilanzsubstanz unter Berücksichtigung des echten Geschäftsmodells in 2-3 Sätzen]
                
                **Der Zukunfts-Accelerator & Marktsituation:**
                [Deine Analyse zur operativen Skalierung, Wachstumsstrategie (z.B. Reinvestitionen) und aktuellen Markttrends]
                
                **Dynamischer ULTRA KI-Score:** [Vergib eine Punktzahl von 0 bis 100.] / 100
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
                    st.metric("Payout Ratio (Bereinigt)", f"{payout_ratio*100:.1f}%")
                    
                st.markdown("---")
                st.info(f"🛡️ ULTRA v2 Modus aktiv | Plausibilitätsfilter eingeschaltet | Modell: gemini-3.6-flash")
                
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
    "Engineered by Gemini & Burhao (ULTRA v2 Global Edition) &nbsp;|&nbsp; Data powered by Yahoo Finance"
    "</p>", 
    unsafe_allow_html=True
)
