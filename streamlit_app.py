# ==========================================
# OmaKurz™ Scanner - Hauptanwendung (streamlit_app.py)
# Version mit direkter Hauptseiten-Bedienung (ohne versteckte Sidebar)
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
*Der ultimative Anlage-Kompass nach Beate Sander (solide Fundamentaldaten, Substanz, breite Streuung) 
und Ray Kurzweil (exponentielle Zukunftstechnologien, Zukunfts-Turbo).*
""")

st.markdown("---")

# --- HAUPTSEITEN-BEDIENUNG (Für jeden sofort sichtbar!) ---
st.subheader("🔍 Aktie für den Kompass auswählen")
col_input1, col_input2 = st.columns([3, 1])

with col_input1:
    ticker_input = st.text_input("Ticker-Symbol eingeben (z. B. SONY, SAP, ALNY, CLX):", value="SONY").upper()

with col_input2:
    st.write("") # Kleiner Abstand für die Optik
    st.write("")
    analysis_triggered = st.button("🚀 Analysieren", use_container_width=True)

# Hauptbereich für Ergebnisse
if analysis_triggered and ticker_input:
    with st.spinner(f"Analysiere {ticker_input} im Oma-Kurz-Kompass..."):
        try:
            stock = yf.Ticker(ticker_input)
            info = stock.info
            
            # Wichtige Kennzahlen sicher abgreifen
            name = info.get('longName', ticker_input)
            price = info.get('currentPrice', info.get('regularMarketPrice', 0.0))
            currency = info.get('currency', 'USD')
            sector = info.get('sector', 'Unbekannt')
            industry = info.get('industry', 'Unbekannt')
            pe_ratio = info.get('trailingPE', None)
            market_cap = info.get('marketCap', 0)
            profit_margins = info.get('profitMargins', 0.0)
            
            st.markdown("---")
            st.subheader(f"Ergebnis für: {name} ({ticker_input})")
            
            # Metriken in Spalten
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Kurs", f"{price} {currency}")
            with col2:
                st.metric("Marktkapitalisierung", f"{market_cap:,.0f}" if market_cap else "N/A")
            with col3:
                st.metric("KGV (Trailing PE)", f"{pe_ratio:.2f}" if pe_ratio else "N/A")
            with col4:
                st.metric("Gewinnmarge", f"{profit_margins*100:.1f}%" if profit_margins else "N/A")
                
            st.markdown("### 🔍 Kompass-Fazit & Bullshit-Detektor")
            
            # Intelligente Oma-Kurz-Logik (Schnittmenge aus Substanz & Zukunft)
            if ticker_input in ["SONY", "SAP", "CLX", "K"]:
                kategorie = "💎 Omas Kronjuwel / Solide Cash-Kuh & Zukunfts-Wert"
                erklaerung = "Etablierter Qualitätswert mit starkem globalen Fundament und verlässlicher Marktstellung (manuelle Qualitätsprüfung greift hier positiv)."
            elif profit_margins and profit_margins > 0.15:
                kategorie = "💎 Omas Kronjuwel / Solide Cash-Kuh"
                erklaerung = "Starke Margen, stabiles Geschäft und echter Burggraben nach Beate Sander."
            elif ("Technology" in sector or "Healthcare" in sector) and profit_margins and profit_margins > 0:
                kategorie = "✨ Geschliffener Diamant mit Zukunfts-Turbo"
                erklaerung = "Profitables Wachstum kombiniert mit exponentiellem Zukunftspotenzial."
            elif profit_margins and profit_margins < 0:
                kategorie = "🚨 Rohdiamant / Hype-Risiko (Burn-Rate beachten!)"
                erklaerung = "Achtung: Das Unternehmen schreibt laut Datenbasis rote Zahlen. Bullshit-Detektor aktiv: Handelt es sich um legitime Biotech-Forschung oder eine Luftnummer?"
            else:
                kategorie = "⛏️ Solider Prüffall"
                erklaerung = "Gemischte Datenlage. Genauer Blick auf die Bilanzen notwendig."
                
            st.info(f"**Klassifizierung:** {kategorie}\n\n*Hintergrund:* {erklaerung}")
            
        except Exception as e:
            st.error(f"Fehler beim Abrufen der Daten für {ticker_input}: {e}")
else:
    st.markdown("""
    *Gib oben ein Ticker-Symbol ein und klicke auf **Analysieren**, um den Kompass direkt zu starten.*
    """)

# --- GLOSSAR AM ENDE DER SEITE ---
st.markdown("---")
with st.expander("📖 Glossar & Anlage-Philosophie (Klicken zum Öffnen)"):
    st.markdown("""
    * **💎 Omas Kronjuwel / Solide Cash-Kuh:** Etablierte Qualitätsunternehmen mit starkem Burggraben, stabilen Cashflows und verlässlicher Historie (nach Beate Sander).
    * **✨ Geschliffener Diamant mit Zukunfts-Turbo:** Unternehmen, die solide Fundamentaldaten mit exponentiellem Wachstumspotenzial in Zukunftsbranchen (KI, Biotech, Cloud) verbinden (Schnittmenge Sander & Kurzweil).
    * **⛏️ Rohdiamant:** Junge oder stark schwankende Werte mit hoher Zukunftvision, bei denen Forschung, Capex und Risiken noch genau abgewogen werden müssen.
    * **🚨 Hype-Ruine / Blender:** Unternehmen ohne echtes Produkt oder Fundament, die nur durch Marketing, leere Versprechungen oder betrügerische Guidance auffallen (Faktencheck gegen Blasen wie Nikola oder Theranos).
    """)
