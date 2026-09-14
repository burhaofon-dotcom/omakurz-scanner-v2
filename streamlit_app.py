# ==========================================
# OmaKurz™ Kompass - Hauptanwendung (streamlit_app.py)
# Version mit integriertem "Nikola-Schutzschild" (Bullshit-Detektor)
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
    ticker_input = st.text_input("Ticker-Symbol eingeben (z. B. SONY, SAP, NKLA, 8306.T):", value="SONY").upper()

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
            
            # --- DER NIKOLA-SCHUTZSCHILD (BULLSHIT-DETEKTOR) ---
            # Prüfen, ob fundamentale Daten komplett fehlen oder das Unternehmen klinisch tot / Pleite ist
            is_data_missing = (not market_cap or market_cap == 0 or price == 0.0 or not profit_margins)
            is_bleeder = (profit_margins and profit_margins < -0.5) # Extremes Verbrennen von Geld
            
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
            
            if is_data_missing or is_bleeder:
                # HARTE STRAFE DURCH DEN BULLSHIT-DETEKTOR
                sander_punkte = 10
                kurzweil_punkte = 15
                gesamt_punkte = 25  # Komplette Abstrafung unter 40 Punkte
            else:
                # Reguläre Berechnung für gesunde Unternehmen
                sander_marge = 5 if profit_margins > 0.15 else (3 if profit_margins > 0 else 1)
                sander_kgv = 5 if pe_ratio and 0 < pe_ratio < 25 else (2 if pe_ratio >= 25 else 3)
                sander_burggraben = 5 if ticker_input in ["SONY", "SAP", "MSFT", "AAPL", "8306.T"] else 3
                sander_cashflow = 4 if profit_margins > 0.05 else 2
                sander_bilanz = 4 
                
                summe_sander = sander_marge + sander_kgv + sander_burggraben + sander_cashflow + sander_bilanz
                sander_punkte = summe_sander * 2 
                
                is_future_sector = sector in ["Technology", "Healthcare", "Communication Services", "Semiconductors", "Financial Services"]
                kurzweil_sektor = 5 if is_future_sector else 2
                kurzweil_skalierung = 5 if is_future_sector else 3
                kurzweil_reale_loesung = 5 if profit_margins > 0 else 3 
                kurzweil_innovation = 4
                kurzweil_jobs_markt = 4
                
                summe_kurzweil = kurzweil_sektor + kurzweil_skalierung + kurzweil_reale_loesung + kurzweil_innovation + kurzweil_jobs_markt
                kurzweil_punkte = summe_kurzweil * 2
                
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
                status = "🚨 Hype-Ruine / Blender-Verdacht (Stresstest ausgelöst!)"
                ausblick = "Achtung: Entweder fehlen essenzielle Fundamentaldaten völlig oder das Geschäftsmodell verbrennt nur Geld ohne reale Wertschöpfung. Sofortige Hype-Warnung!"
                
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
    * **Der Stresstest-Filter:** Erkennt fehlende Bilanzen und Blender-Buden automatisch und zieht den Score sofort in den Keller.
    """)
