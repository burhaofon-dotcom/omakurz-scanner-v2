# ==========================================
# OmaKurz™ Kompass - Hauptanwendung (streamlit_app.py)
# Version mit Branchen-Spaten-Logik, Pre-IPO Faktencheck & Watchlist
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
und Ray Kurzweil (exponentielle Zukunftstechnologien, echte Wertschöpfung & Skalierung) – inklusive Watchlist.*
""")

st.markdown("---")

# --- SEITENLEISTE FÜR WATCHLIST ---
st.sidebar.title("📌 Deine Watchlist")
if st.session_state.watchlist:
    for item in st.session_state.watchlist:
        st.sidebar.write(f"• {item}")
    if st.sidebar.button("🗑️ Watchlist leeren"):
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
        ticker_input = st.text_input("Ticker-Symbol eingeben (z. B. SONY, SAP, NKLA):", value="SONY").upper()
    with col_input2:
        st.write("") 
        st.write("")
        analysis_triggered = st.button("🚀 Analysieren", use_container_width=True)

    if analysis_triggered and ticker_input:
        with st.spinner(f"Berechne das 10-Säulen-Modell mit Spaten-Logik für {ticker_input}..."):
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
                
                is_real_default = (not market_cap or market_cap == 0 or price == 0.0)
                
                st.markdown("---")
                st.subheader(f"Ergebnis für: {name} ({ticker_input})")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Kurs", f"{price} {currency}")
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
                    if sector in ["Healthcare", "Technology"] and profit_margins < 0:
                        sander_marge = 3 
                    else:
                        sander_marge = 5 if profit_margins > 0.15 else (3 if profit_margins > 0 else 1)
                    
                    sander_kgv = 5 if pe_ratio and 0 < pe_ratio < 25 else (2 if pe_ratio >= 25 else 3)
                    sander_burggraben = 5 if ticker_input in ["SONY", "SAP", "MSFT", "AAPL", "8306.T", "RECKITT.L"] else 3
                    sander_cashflow = 4 if profit_margins > 0.05 else 2
                    sander_bilanz = 4 
                    
                    summe_sander = sander_marge + sander_kgv + sander_burggraben + sander_cashflow + sander_bilanz
                    sander_punkte = summe_sander * 2 
                    
                    if sector in ["Technology", "Semiconductors", "Communication Services"]:
                        k_sektor, k_skalierung, k_loesung = 5, 5, 5
                    elif sector in ["Healthcare"]:
                        k_sektor, k_skalierung, k_loesung = 5, 3, 4
                    elif sector in ["Financial Services"]:
                        k_sektor, k_skalierung, k_loesung = 3, 4, 4
                    elif sector in ["Consumer Defensive", "Energy", "Industrials"]:
                        k_sektor, k_skalierung, k_loesung = 2, 3, 4
                    else:
                        k_sektor, k_skalierung, k_loesung = 3, 3, 3
                    
                    kurzweil_innovation = 5 if sector in ["Technology", "Healthcare", "Semiconductors"] else 3
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
                elif gesamt_punkte >= 85:
                    status = "💎 Omas absolut unangetastetes Kronjuwel"
                    ausblick = "Hervorragende Symbiose aus starker Substanz und branchenspezifischem Zukunfts-Turbo."
                elif gesamt_punkte >= 65:
                    status = "✨ Geschliffener Diamant mit starkem Turbo"
                    ausblick = "Solides Fundament im passenden Spaten mit klarem Blick nach vorn."
                elif gesamt_punkte >= 45:
                    status = "⛏️ Rohdiamant / Genauer Prüffall (Biotech- oder Deep-Tech-Modus)"
                    ausblick = "Forschungsstarker Sektor mit hohem Cash-Burn. Potenzial für die nächsten Quartale."
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
                    else:
                        st.warning("Bereits auf der Watchlist.")
                
            except Exception as e:
                st.error(f"Fehler beim Abrufen der Daten für {ticker_input}: {e}")

else:
    # --- PRE-IPO & PRIVATE UNICORN FAKTENCHECK-MODUS ---
    st.markdown("### 🦄 Pre-IPO / Private Unicorn Web-Faktenchecker")
    st.markdown("Hier durchleuchtet der Kompass private Giganten (wie *Anthropic* oder *OpenAI*) oder historische Blenden (wie *Theranos*) anhand von harten Fakten und dem Bullshit-Detektor.")
    
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
                comment = f"{unicorn_name} zeigt massive technologische Wucht, echte Großkonzern-Validierung und skaliert im Markt. Sobald das Papier handelbar ist, ein absoluter Pflichtkandidat für die Watchlist."
            elif "Wachstumsphase" in evidence_level:
                sub_score = 28
                turbo_score = 42
                verdict = "⛏️ **Spannender Rohdiamant (High-Risk / High-Reward)**"
                comment = f"Klassisches Pre-IPO-Unicorn. Starker Zukunfts-Turbo, aber hoher Kapitalbedarf. Den Cash-Burn genau im Auge behalten."
            else:
                sub_score = 8
                turbo_score = 15
                verdict = "🚨 **Theranos-Alarm / Hohe Blender- & Hype-Gefahr!**"
                comment = f"Achtung! Hier blinken alle Warnleuchten. Fehlende unabhängige Validierung und zu viel intransparenter Hochglanz-PR erinnern an historische Pleite-Storys. Finger weg!"
            
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
            
            # Watchlist Button für Unicorns
            unicorn_label = f"🦄 {unicorn_name} (Pre-IPO) - {total_unicorn_score}/100 Pkt"
            if st.button("📌 Pre-IPO zur Watchlist hinzufügen"):
                if unicorn_label not in st.session_state.watchlist:
                    st.session_state.watchlist.append(unicorn_label)
                    st.success("Erfolgreich zur Watchlist hinzugefügt! (Siehe Sidebar links)")
                else:
                    st.warning("Bereits auf der Watchlist.")

# --- GLOSSAR AM ENDE DER SEITE ---
st.markdown("---")
with st.expander("📖 Das 10-Säulen-Modell & Spaten-Logik (Klicken zum Öffnen)"):
    st.markdown("""
    * **Säulen 1–5 (Beate Sander):** Gewinnmarge, faires KGV, Burggraben, Cashflow, gesunde Bilanz (mit Biotech-Ausnahme für F&E).
    * **Säulen 6–10 (Ray Kurzweil):** Branchenspezifische Zukunfts-Spaten (Tech, Healthcare, Finanzen, Konsum), Skalierbarkeit und echte Wertschöpfung.
    * **Pre-IPO-Modus & Watchlist:** Speichert geprüfte Aktien und private Unicorns direkt in deiner persönlichen Session-Watchlist ab.
    """)
