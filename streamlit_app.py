# ==========================================
# OmaKurz™ Kompass - Hauptanwendung (streamlit_app.py)
# Version mit automatischer Branchen-Spaten-Logik & Stresstest-Schutzschild
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

# Titel & Philosophie
st.title("🧭 Oma-Kurz-Kompass")
st.markdown("""
*Der ultimative Anlage-Kompass nach Beate Sander (solide Fundamentaldaten, Substanz, Dividenden) 
und Ray Kurzweil (exponentielle Zukunftstechnologien, echte Wertschöpfung & Skalierung) – mit branchenspezifischer Spaten-Logik.*
""")

st.markdown("---")

# --- HAUPTSEITEN-BEDIENUNG ---
st.subheader("🔍 Aktie oder IPO-Kandidat für den Kompass auswählen")
col_input1, col_input2 = st.columns([3, 1])

with col_input1:
    ticker_input = st.text_input("Ticker-Symbol eingeben (z. B. SONY, SAP, NKLA, KYG4790P1037):", value="SONY").upper()

with col_input2:
    st.write("") 
    st.write("")
    analysis_triggered = st.button("🚀 Analysieren", use_container_width=True)

# Hauptbereich für Ergebnisse
if analysis_triggered and ticker_input:
    with st.spinner(f"Berechne das 10-Säulen-Modell mit Spaten-Logik für {ticker_input}..."):
        try:
            stock = yf.Ticker(ticker_input)
            info = stock.info
            
            # Wichtige Kennzahlen abgreifen
            name = info.get('longName', ticker_input)
            price = info.get('currentPrice', info.get('regularMarketPrice', 0.0))
            currency = info.get('currency', 'USD')
            sector = info.get('sector', 'Unbekannt')
            industry = info.get('industry', 'Unbekannt')
            pe_ratio = info.get('trailingPE', 0)
            market_cap = info.get('marketCap', 0)
            profit_margins = info.get('profit_margins', info.get('profitMargins', 0.0))
            
            # --- 1. DER NIKOLA-SCHUTZSCHILD (BULLSHIT-DETEKTOR) ---
            # Harte Pleite-Prüfung: Wenn Kurs 0 oder keine Marktkapitalisierung existiert -> Sofortiger Stresstest!
            is_real_default = (not market_cap or market_cap == 0 or price == 0.0)
            
            st.markdown("---")
            st.subheader(f"Ergebnis für: {name} ({ticker_input})")
            
            # Metriken in Spalten
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Kurs", f"{price} {currency}")
            with col2:
                st.metric("Marktkapitalisierung", f"{market_cap:,.0f}" if market_cap else "N/A")
            with col3:
                st.metric("KGV (Trailing PE)", f"{pe_ratio:.2f}" if pe_ratio and pe_ratio > 0 else "N/A")
            with col4:
                st.metric("Gewinnmarge", f"{profit_margins*100:.1f}%" if profit_margins else "N/A")
                
            st.markdown(f"**Ererkannte Branche (Spaten-Logik):** *{sector} / {industry}*")
            st.markdown("### 📊 Das 10-Säulen-Punktesystem (Max. 100 Punkte)")
            
            if is_real_default:
                # --- STRESSTEST AUSGELÖST (Wie bei Nikola) ---
                sander_punkte = 10
                kurzweil_punkte = 15
                gesamt_punkte = 25  
                spaten_status = "🚨 Hype-Ruine / Pleitegefahr"
            else:
                # --- 2. DIE BRANCHEN-SPATEN-LOGIK ---
                
                # A. Sander-Bewertung (Substanz & Stabilität)
                if sector in ["Healthcare", "Technology"] and profit_margins < 0:
                    # Biotech / Deep-Tech Startups dürfen in der Forschungsphase negative Margen haben
                    sander_marge = 3 # Neutraler Punkt für F&E-Investition statt Totalabzug
                else:
                    sander_marge = 5 if profit_margins > 0.15 else (3 if profit_margins > 0 else 1)
                
                sander_kgv = 5 if pe_ratio and 0 < pe_ratio < 25 else (2 if pe_ratio >= 25 else 3)
                sander_burggraben = 5 if ticker_input in ["SONY", "SAP", "MSFT", "AAPL", "8306.T", "RECKITT.L"] else 3
                sander_cashflow = 4 if profit_margins > 0.05 else 2
                sander_bilanz = 4 
                
                summe_sander = sander_marge + sander_kgv + sander_burggraben + sander_cashflow + sander_bilanz
                sander_punkte = summe_sander * 2 # Skalierung auf 50 Max-Punkte
                
                # B. Kurzweil-Bewertung (Zukunft & Skalierung nach Spaten)
                if sector in ["Technology", "Semiconductors", "Communication Services"]:
                    # High-Speed Software & Tech
                    k_sektor, k_skalierung, k_loesung = 5, 5, 5
                elif sector in ["Healthcare"]:
                    # Biotech & Pharma (Lange Zyklen, aber exponentielles Potenzial bei Durchbrüchen)
                    k_sektor, k_skalierung, k_loesung = 5, 3, 4
                elif sector in ["Financial Services"]:
                    # Banken & Fintechs
                    k_sektor, k_skalierung, k_loesung = 3, 4, 4
                elif sector in ["Consumer Defensive", "Energy", "Industrials"]:
                    # Klassische Industrie, Konsum, Tabak (Defensiver Spaten)
                    k_sektor, k_skalierung, k_loesung = 2, 3, 4
                else:
                    # Standard-Fallback für unbekannte Spaten
                    k_sektor, k_skalierung, k_loesung = 3, 3, 3
                
                kurzweil_innovation = 5 if sector in ["Technology", "Healthcare", "Semiconductors"] else 3
                kurzweil_jobs_markt = 4
                
                summe_kurzweil = k_sektor + k_skalierung + k_loesung + kurzweil_innovation + kurzweil_jobs_markt
                kurzweil_punkte = summe_kurzweil * 2 # Skalierung auf 50 Max-Punkte
                
                gesamt_punkte = sander_punkte + kurzweil_punkte
                
            # Punkte-Anzeige in UI
            pcol1, pcol2, pcol3 = st.columns(3)
            with pcol1:
                st.metric("👵 Sander-Punkte (Substanz)", f"{sander_punkte} / 50")
            with pcol2:
                st.metric("🚀 Kurzweil-Punkte (Zukunft)", f"{kurzweil_punkte} / 50")
            with pcol3:
                st.metric("🎯 Gesamt-Score", f"{gesamt_punkte} / 100")
                
            # Fortschrittsbalken für den Score
            st.progress(gesamt_punkte / 100)
            
            # Bewertung & Zeithorizont-Ausblick (36 Monate)
            st.markdown("### 🧭 Kompass-Fazit & 36-Monats-Prognose")
            
            if is_real_default:
                status = "🚨 Hype-Ruine / Pleitegefahr (Stresstest ausgelöst!)"
                ausblick = "Achtung: Grundlegende Marktdaten fehlen oder das Unternehmen ist klinisch insolvent. Sofortige Hype-Warnung nach Nikola-Muster!"
            elif gesamt_punkte >= 85:
                status = "💎 Omas absolut unangetastetes Kronjuwel"
                ausblick = "Hervorragende Symbiose aus starker Substanz und branchenspezifischem Zukunfts-Turbo. Perfekt für den langfristigen 36-Monats-Aufbau."
            elif gesamt_punkte >= 65:
                status = "✨ Geschliffener Diamant mit starkem Turbo"
                ausblick = "Solides Fundament im passenden Spaten mit klarem Blick nach vorn. Guter Rückenwind für die nächsten 36 Monate."
            elif gesamt_punkte >= 45:
                status = "⛏️ Rohdiamant / Genauer Prüffall (Biotech- oder Deep-Tech-Modus)"
                ausblick = "Forschungsstarker Sektor mit hohem Cash-Burn. Substanz zieht zwar Punkte ab, aber der Zukunftsfaktor bietet Potenzial für die nächsten Quartale."
            else:
                status = "⚠️ Schwacher Trend / Vorsicht geboten"
                ausblick = "Weder überzeugende Substanz noch starker Zukunfts-Turbo. In den nächsten 36 Monaten eher ein Risiko-Investment."
                
            st.info(f"**Klassifizierung:** {status}\n\n**36-Monats-Fokus:** {ausblick}")
            
        except Exception as e:
            st.error(f"Fehler beim Abrufen der Daten für {ticker_input}: {e}")
else:
    st.markdown("""
    *Gib oben ein Ticker-Symbol ein und klicke auf **Analysieren**, um das 10-Säulen-Modell mit Spaten-Logik zu starten.*
    """)

# --- GLOSSAR AM ENDE DER SEITE ---
st.markdown("---")
with st.expander("📖 Das 10-Säulen-Modell & Spaten-Logik (Klicken zum Öffnen)"):
    st.markdown("""
    * **Säulen 1–5 (Beate Sander):** Gewinnmarge, faires KGV, Burggraben, Cashflow, gesunde Bilanz (mit Biotech-Ausnahme für F&E).
    * **Säulen 6–10 (Ray Kurzweil):** Branchenspezifische Zukunfts-Spaten (Tech, Healthcare, Finanzen, Konsum), Skalierbarkeit und echte Wertschöpfung.
    * **Der Stresstest-Filter:** Schützt vor Pleite-Buden (Nikola-Schutzschild) bei fehlenden Marktdaten.
    """)
