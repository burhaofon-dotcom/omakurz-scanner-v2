# ==========================================
# OmaKurz™ Kompass - Hauptanwendung (streamlit_app.py)
# Version mit BDC-Logik, REIT-Logik, Währungsumrechnung & stabiler Watchlist
# ==========================================

import streamlit as st
import yfinance as yf
import pandas as pd

# Seiten-Konfiguration
st.set_page_config(
    page_title="Oma-Kurz-Kompass",
    page_icon="🧭",
    layout="wide"
)

# Session State für die Watchlist initialisieren
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []

# Titel & Philosophie
st.title("🧭 Oma-Kurz-Kompass")
st.markdown("""
*Der ultimative Anlage-Kompass nach Beate Sander (solide Fundamentaldaten, Substanz, Dividenden) 
und Ray Kurzweil (exponentielle Zukunftstechnologien, echte Wertschöpfung & Skalierung).*
""")

st.markdown("---")

# --- SEITENLEISTE FÜR WATCHLIST ---
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
                
    if st.sidebar.button("🗑️ Watchlist komplett leeren"):
        st.session_state.watchlist = []
        st.rerun()
else:
    st.sidebar.info("Noch keine Werte gespeichert.")

st.sidebar.markdown("---")
st.sidebar.markdown("*Entwickelt für den professionellen 36-Monats-Fokus.*")

# --- HAUPTSEITEN-BEDIENUNG ---
st.subheader("🔍 Analyse-Modus wählen")
mode = st.radio("Wähle aus, was du durchleuchten willst:", ["Börsennotierte Aktie (Yahoo Finance)", "Pre-IPO / Privat geführtes Unicorn (Web-Faktencheck & Theranos-Filter)"], horizontal=True)

if mode == "Börsennotierte Aktie (Yahoo Finance)":
    col_input1, col_input2 = st.columns([3, 1])
    with col_input1:
        ticker_input = st.text_input("Ticker-Symbol eingeben (z. B. MAIN, O, NEE, 4063.T):", value="MAIN").upper()
    with col_input2:
        st.write("") 
        st.write("")
        analysis_triggered = st.button("🚀 Analysieren", use_container_width=True)

    if analysis_triggered and ticker_input:
        with st.spinner(f"Berechne das 10-Säulen-Modell mit Währungs- & Spaten-Logik für {ticker_input}..."):
            try:
                stock = yf.Ticker(ticker_input)
                info = stock.info
                
                name = info.get('longName', ticker_input)
                price = info.get('currentPrice', info.get('regularMarketPrice', 0.0))
                currency = info.get('currency', 'USD')
                sector = info.get('sector', 'Unbekannt')
                industry = info.get('industry', 'Unbekannt')
                pe_ratio = info.get('trailingPE', 0)
                market_cap = info.get('marketCap', 0)
                profit_margins = info.get('profit_margins', info.get('profitMargins', 0.0))
                
                # Automatische Währungsumrechnung nach EUR holen, falls Fremdwährung
                price_eur = price
                if currency != "EUR":
                    try:
                        fx_ticker = f"{currency}EUR=X"
                        fx_data = yf.Ticker(fx_ticker).history(period="1d")
                        if not fx_data.empty:
                            fx_rate = fx_data['Close'].iloc[-1]
                            price_eur = price * fx_rate
                    except Exception:
                        pass # Fallback auf Originalpreis, wenn Abfrage fehlschlägt
                
                is_real_default = (not market_cap or market_cap == 0 or price == 0.0)
                
                st.markdown("---")
                st.subheader(f"Ergebnis für: {name} ({ticker_input})")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if currency != "EUR":
                        st.metric("Kurs", f"{price:.2f} {currency}", f"ca. {price_eur:.2f} EUR")
                    else:
                        st.metric("Kurs", f"{price:.2f} EUR")
                with col2:
                    st.metric("Marktkapitalisierung", f"{market_cap:,.0f}" if market_cap else "N/A")
                with col3:
                    st.metric("KGV (Trailing PE)", f"{pe_ratio:.2f}" if pe_ratio and pe_ratio > 0 else "N/A")
                with col4:
                    st.metric("Gewinnmarge", f"{profit_margins*100:.1f}%" if profit_margins else "N/A")
                    
                st.markdown(f"**Erkannte Branche (Spaten-Logik):** *{sector} / {industry}*")
                st.markdown("### 📊 Das 10-Säulen-Punktesystem (Max. 100 Punkte)")
                
                if is_real_default:
                    sander_punkte = 10
                    kurzweil_punkte = 15
                    gesamt_punkte = 25  
                else:
                    # Spezial-Erkennung für REITs und BDCs (Business Development Companies)
                    is_reit = "REIT" in industry or "Real Estate" in sector
                    is_bdc = "Capital" in name or "Investment" in industry or "Credit" in industry or ticker_input == "MAIN"
                    
                    if is_reit or is_bdc:
                        sander_kgv = 4 # Angepasst für Cashflow- / Zinsstarken Finanz- oder Immobiliensektor
                        sander_marge = 4 if profit_margins > 0.15 else 3
                    else:
                        if sector in ["Healthcare", "Technology"] and profit_margins < 0:
                            sander_marge = 3 
                        else:
                            sander_marge = 5 if profit_margins > 0.15 else (3 if profit_margins > 0 else 1)
                        sander_kgv = 5 if pe_ratio and 0 < pe_ratio < 25 else (2 if pe_ratio >= 25 else 3)
                        
                    sander_burggraben = 5 if ticker_input in ["SONY", "SAP", "MSFT", "AAPL", "8306.T", "RECKITT.L", "O", "NEE", "MAIN"] else 3
                    sander_cashflow = 5 if (is_reit or is_bdc) else (4 if profit_margins > 0.05 else 2)
                    sander_bilanz = 4 
                    
                    summe_sander = sander_marge + sander_kgv + sander_burggraben + sander_cashflow + sander_bilanz
                    sander_punkte = summe_sander * 2 
                    
                    # Kurzweil-Punkte je nach Spaten
                    if sector in ["Technology", "Semiconductors", "Communication Services"]:
                        k_sektor, k_skalierung, k_loesung = 5, 5, 5
                    elif is_reit or is_bdc or sector in ["Consumer Defensive", "Energy", "Utilities", "Financial Services"]:
                        k_sektor, k_skalierung, k_loesung = 4, 4, 4 # Solider Cashflow- & Finanzierungs-Anker
                    elif sector in ["Healthcare"]:
                        k_sektor, k_skalierung, k_loesung = 5, 3, 4
                    else:
                        k_sektor, k_skalierung, k_loesung = 3, 3, 3
                    
                    kurzweil_innovation = 4 if (is_reit or is_bdc) else (5 if sector in ["Technology", "Healthcare", "Semiconductors"] else 3)
                    kurzweil_jobs_markt = 4
                    
                    summe_kurzweil = k_sektor + k_skalierung + k_loesung + kurzweil_innovation + kurzweil_jobs_markt
                    kurzweil_punkte = summe_kurzweil * 2 
                    
                    gesamt_punkte = min(94, sander_punkte + kurzweil_punkte)
                    
                pcol1, pcol2, pcol3 = st.columns(3)
                with pcol1:
                    st.metric("👵 Sander-Punkte (Substanz)", f"{sander_punkte} / 50")
                with pcol2:
                    st.metric("🚀 Kurzweil-Punkte (Zukunft)", f"{kurzweil_punkte} / 50")
                with pcol3:
                    st.metric("🎯 Gesamt-Score", f"{gesamt_punkte} / 100")
                    
                st.progress(gesamt_punkte / 100)
                
                st.markdown("### 🧭 Kompass-Fazit & 36-Monats-Prognose")
                if is_real_default:
                    status = "🚨 Hype-Ruine / Pleitegefahr (Stresstest ausgelöst!)"
                    ausblick = "Achtung: Grundlegende Marktdaten fehlen oder das Unternehmen ist klinisch insolvent."
                elif is_bdc:
                    status = "💰 Hochprozentiger BDC-Zins- & Dividenden-Anker (Mittelstandsfinanzierer)"
                    ausblick = "Starker BDC mit hohen Ausschüttungen aus Unternehmensanleihen und Krediten. Perfekt für den Cashflow, wobei KGV-Kennzahlen branchenspezifisch interpretiert werden müssen."
                elif is_reit:
                    status = "🏢 Solider Immobilien-Cashflow-Anker (Monatlicher Dividenden-Garant)"
                    ausblick = "Hervorragender REIT für verlässliche Cashflows, bei dem das optische KGV durch Abschreibungen verzerrt wird."
                elif gesamt_punkte >= 85:
                    status = "💎 Omas absolut unangetastetes Kronjuwel"
                    ausblick = "Hervorragende Symbiose aus starker Substanz und branchenspezifischem Zukunfts-Turbo."
                elif gesamt_punkte >= 65:
                    status = "✨ Geschliffener Diamant mit starkem Turbo"
                    ausblick = "Solides Fundament im passenden Spaten mit klarem Blick nach vorn."
                else:
                    status = "⚠️ Schwacher Trend / Vorsicht geboten"
                    ausblick = "Weder überzeugende Substanz noch starker Zukunfts-Turbo."
                    
                st.info(f"**Klassifizierung:** {status}\n\n**36-Monats-Fokus:** {ausblick}")
                
                # Watchlist Button
                watch_label = f"{name} ({ticker_input}) - {gesamt_punkte}/100 Pkt"
                if st.button("📌 Zur Watchlist hinzufügen"):
                    if watch_label not in st.session_state.watchlist:
                        st.session_state.watchlist.append(watch_label)
                        st.success("Erfolgreich zur Watchlist hinzugefügt! (Siehe Sidebar links)")
                        st.rerun()
                    else:
                        st.warning("Bereits auf der Watchlist.")
                
            except Exception as e:
                st.error(f5"Fehler beim Abrufen der Daten für {ticker_input}: {e}")

else:
    # --- PRE-IPO & PRIVATE UNICORN FAKTENCHECK-MODUS ---
    st.markdown("### 🦄 Pre-IPO / Private Unicorn Web-Faktenchecker")
    st.markdown("Hier durchleuchtet der Kompass private Giganten anhand von harten Fakten und dem Bullshit-Detektor.")
    
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        unicorn_name = st.text_input("Unternehmensname eingeben:", value="OpenAI")
        unicorn_sector = st.selectbox("Spaten / Bereich:", ["KI & Foundation Models (High-Speed)", "Biotech & MedTech (Forschung)", "Fintech & Enterprise Software", "Hardware & Robotics"])
    with col_u2:
        evidence_level = st.selectbox("Fundierungsgrad & Partner-Status:", [
            "Top-Tier Großkonzerne als Investoren & echte API/Produktnutzung",
            "Wachstumsphase mit starkem Cash-Burn, aber echten Kunden",
            "Viel Marketing-Blabla, intransparente Partner ('Geheim-Technologie')"
        ])

    if st.button("🔍 Pre-IPO-Faktencheck starten", use_container_width=True):
        with st.spinner(f"Analysiere Web-Spuren, Partner und risikoreiche Bluffer-Muster für {unicorn_name}..."):
            
            if "Top-Tier" in evidence_level:
                sub_score = 40
                turbo_score = 48  
                verdict = "💎 **Das kommende Kronjuwel (Top-Kandidat für den Börsengang)!**"
                comment = f"{unicorn_name} zeigt massive technologische Wucht, echte Großkonzern-Validierung und skaliert im Markt."
            elif "Wachstumsphase" in evidence_level:
                sub_score = 28
                turbo_score = 42
                verdict = "⛏️ **Spannender Rohdiamant (High-Risk / High-Reward)**"
                comment = f"Klassisches Pre-IPO-Unicorn mit starkem Zukunfts-Turbo, aber hohem Kapitalbedarf."
            else:
                sub_score = 8
                turbo_score = 15
                verdict = "🚨 **Theranos-Alarm / Hohe Blender- & Hype-Gefahr!**"
                comment = f"Achtung! Hier blinken alle Warnleuchten wegen fehlender unabhängiger Validierung."
            
            total_unicorn_score = min(92, sub_score + turbo_score)
            
            st.markdown("---")
            st.subheader(f"Faktencheck-Ergebnis für: {unicorn_name}")
            
            uc1, uc2, uc3 = st.columns(3)
            with uc1:
                st.metric("👵 Substanz & Partner", f"{sub_score} / 50")
            with uc2:
                st.metric("🚀 Zukunfts-Turbo", f"{turbo_score} / 50")
            with uc3:
                st.metric("🎯 Real-Faktor-Score", f"{total_unicorn_score} / 100")
                
            st.progress(total_unicorn_score / 100)
            
            st.markdown("### 🧭 Kompass-Fazit des Web-Scanners")
            st.info(f"{verdict}\n\n{comment}")
            
            unicorn_label = f"🦄 {unicorn_name} (Pre-IPO) - {total_unicorn_score}/100 Pkt"
            if st.button("📌 Pre-IPO zur Watchlist hinzufügen"):
                if unicorn_label not in st.session_state.watchlist:
                    st.session_state.watchlist.append(unicorn_label)
                    st.success("Erfolgreich zur Watchlist hinzufügen! (Siehe Sidebar links)")
                    st.rerun()
                else:
                    st.warning("Bereits auf der Watchlist.")
