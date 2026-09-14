# ==========================================
# OmaKurz™ Kompass - Hauptanwendung (streamlit_app.py)
# Version mit dem 10-Säulen-Punktesystem (Sander & Kurzweil)
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
und Ray Kurzweil (exponentielle Zukunftstechnologien, echte Wertschöpfung & Skalierung).*
""")

st.markdown("---")

# --- HAUPTSEITEN-BEDIENUNG ---
st.subheader("🔍 Aktie für den Kompass auswählen")
col_input1, col_input2 = st.columns([3, 1])

with col_input1:
    ticker_input = st.text_input("Ticker-Symbol eingeben (z. B. SONY, SAP, ALNY, CLX):", value="SONY").upper()

with col_input2:
    st.write("") 
    st.write("")
    analysis_triggered = st.button("🚀 Analysieren", use_container_width=True)

# Hauptbereich für Ergebnisse
if analysis_triggered and ticker_input:
    with st.spinner(f"Berechne das 10-Säulen-Modell für {ticker_input}..."):
        try:
            stock = yf.Ticker(ticker_input)
            info = stock.info
            
            # Wichtige Kennzahlen abgreifen
            name = info.get('longName', ticker_input)
            price = info.get('currentPrice', info.get('regularMarketPrice', 0.0))
            currency = info.get('currency', 'USD')
            sector = info.get('sector', 'Unbekannt')
            pe_ratio = info.get('trailingPE', 0)
            market_cap = info.get('marketCap', 0)
            profit_margins = info.get('profit_margins', info.get('profitMargins', 0.0))
            
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
                
            st.markdown("### 📊 Das 10-Säulen-Punktesystem (Max. 100 Punkte)")
            
            # --- DIE OMA-KURZ-FORMEL (10 Säulen, je 1-5 Punkte) ---
            # Beispielhafte algorithmische Ableitung aus den Live-Daten & Sektoren
            
            # 1. Beate Sander Säulen (Fundament & Substanz)
            sander_marge = 5 if profit_margins and profit_margins > 0.15 else (3 if profit_margins and profit_margins > 0 else 1)
            sander_kgv = 5 if pe_ratio and 0 < pe_ratio < 25 else (2 if pe_ratio and pe_ratio >= 25 else 3)
            sander_burggraben = 5 if ticker_input in ["SONY", "SAP", "CLX", "MSFT", "AAPL"] else 3
            sander_cashflow = 4 if profit_margins and profit_margins > 0.05 else 2
            sander_bilanz = 4 # Solider Standard-Wert für etablierte Werte
            
            summe_sander = sander_marge + sander_kgv + sander_burggraben + sander_cashflow + sander_bilanz # Max 25 (wir skalieren auf 50)
            sander_punkte = summe_sander * 2 
            
            # 2. Ray Kurzweil Säulen (Zukunfts-Turbo & Skalierung)
            is_future_sector = sector in ["Technology", "Healthcare", "Communication Services", "Semiconductors"]
            kurzweil_sektor = 5 if is_future_sector else 2
            kurzweil_skalierung = 5 if is_future_sector else 3
            kurzweil_reale_loesung = 5 if profit_margins and profit_margins > 0 else 3 # Kein reiner Verlust-Hype
            kurzweil_innovation = 4
            kurzweil_jobs_markt = 4
            
            summe_kurzweil = kurzweil_sektor + kurzweil_skalierung + kurzweil_reale_loesung + kurzweil_innovation + kurzweil_jobs_markt # Max 25 (skaliert auf 50)
            kurzweil_punkte = summe_kurzweil * 2
            
            # Gesamtpunktzahl (0 - 100)
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
            
            if gesamt_punkte >= 85:
                status = "💎 Omas absolut unangetastetes Kronjuwel"
                ausblick = "Hervorragende Symbiose aus starker Substanz und exponentiellem Zukunfts-Turbo. Perfekt für den langfristigen 36-Monats-Aufbau ohne Nachtschicht-Sorgen."
            elif gesamt_punkte >= 65:
                status = "✨ Geschliffener Diamant mit starkem Turbo"
                ausblick = "Solides Fundament mit klarem Blick nach vorn. In den nächsten 36 Monaten mit solidem Rückenwind durch technologische Skalierung zu erwarten."
            elif gesamt_punkte >= 45:
                status = "⛏️ Rohdiamant / Genauer Prüffall"
                ausblick = "Spannender Ansatz, aber entweder hinkt die Substanz oder der Zukunftsfaktor ist noch nicht sauber monetarisiert. Genauer Blick auf die nächsten Quartale nötig."
            else:
                status = "🚨 Hype-Ruine / Zu hohes Risiko"
                ausblick = "Achtung: Erfüllt weder Omas Substanz-Kriterien noch Kurzweils saubere Wertschöpfung. Finger weg."
                
            st.info(f"**Klassifizierung:** {status}\n\n**36-Monats-Fokus:** {ausblick}")
            
        except Exception as e:
            st.error(f"Fehler beim Abrufen der Daten für {ticker_input}: {e}")
else:
    st.markdown("""
    *Gib oben ein Ticker-Symbol ein und klicke auf **Analysieren**, um das 10-Säulen-Modell zu starten.*
    """)

# --- GLOSSAR AM ENDE DER SEITE ---
st.markdown("---")
with st.expander("📖 Das 10-Säulen-Modell (Klicken zum Öffnen)"):
    st.markdown("""
    * **Säulen 1–5 (Beate Sander):** Gewinnmarge, faires KGV, Burggraben/Krisenfestigkeit, Cashflow/Dividendenstärke, gesunde Bilanz.
    * **Säulen 6–10 (Ray Kurzweil):** Exponentieller Zukunftssektor, echte technologische Skalierbarkeit, reale Wertschöpfung (keine reine Burn-Rate), Innovationskraft, nachhaltiger Marktwert.
    * **Der 36-Monats-Horizont:** Schaut über das kurzfristige Rauschen hinweg und bewertet die Ertragskraft im Takt des technologischen Fortschritts.
    """)
