# ==========================================
# OmaKurz™ Scanner - Hauptanwendung (streamlit_app.py)
# ==========================================

import streamlit as st
import yfinance as yf
import pandas as pd

# Hilfsfunktionen importieren (falls vorhanden)
try:
    from omakurz_helpers import safe_float, clean_series
except ImportError:
    # Fallback, falls Helfer nicht direkt greifen
    def safe_float(val):
        try:
            return float(val)
        except:
            return 0.0

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

# Sidebar für Eingaben
st.sidebar.header("🎛️ Scanner-Steuerung")
ticker_input = st.sidebar.text_input("Ticker-Symbol eingeben (z. B. ALNY, SONY, SAP, CLX):", value="SONY").upper()

# Analyse-Button in der Sidebar oder Hauptseite
analysis_triggered = st.sidebar.button("🚀 Aktie analysieren & bewerten")

# Hauptbereich
if analysis_triggered and ticker_input:
    with st.spinner(f"Analysiere {ticker_input} durch den Oma-Kurz-Kompass..."):
        try:
            stock = yf.Ticker(ticker_input)
            info = stock.info
            
            name = info.get('longName', ticker_input)
            price = info.get('currentPrice', info.get('regularMarketPrice', 0.0))
            currency = info.get('currency', 'USD')
            sector = info.get('sector', 'Unbekannt')
            industry = info.get('industry', 'Unbekannt')
            
            st.subheader(f"Ergebnis für: {name} ({ticker_input})")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Aktueller Preis", f"{price} {currency}")
            with col2:
                st.metric("Sektor", sector)
            with col3:
                st.metric("Branche", industry)
                
            st.markdown("---")
            st.markdown("### 🔍 Kompass-Fazit & Bewertung")
            
            # Beispielhafte Logik für die Einordnung (wird später vollautomatisiert)
            if "Technology" in sector or "Healthcare" in sector or ticker_input in ["ALNY", "SONY", "SAP"]:
                kategorie = "✨ Geschliffener Diamant mit Zukunfts-Turbo"
                erklaerung = "Vereint technologische Innovationskraft / Zukunfts-Plattform mit echtem wirtschaftlichem Fundament."
            elif "Consumer" in sector or "Utilities" in sector:
                kategorie = "💎 Omas Kronjuwel / Solide Cash-Kuh"
                erklaerung = "Klassischer Substanzwert mit starkem Burggraben, ideal für den langfristigen Vermögensaufbau und verlässliche Stabilität."
            else:
                kategorie = "⛏️ Rohdiamant / Prüffall"
                erklaerung = "Interessantes Geschäftsmodell, das genauer auf Cashflows und operative Stabilität geprüft werden muss."
                
            st.info(f"**Klassifizierung:** {kategorie}\n\n*Hintergrund:* {erklaerung}")
            
        except Exception as e:
            st.error(f"Fehler beim Abrufen der Daten für {ticker_input}: {e}")
else:
    st.markdown("""
    ### 👋 Willkommen zurück!
    Gib links ein Ticker-Symbol ein (z. B. **SONY**, **SAP**, **ALNY** für Alnylam oder **CLX** für Clorox) und klicke auf **Aktie analysieren**, um den Kompass zu starten.
    """)

# --- GLOSSAR AM ENDE DER SEITE ---
st.markdown("---")
with st.expander("📖 Glossar & Anlage-Philosophie (Klicken zum Öffnen)"):
    st.markdown("""
    * **💎 Omas Kronjuwel / Solide Cash-Kuh:** Etablierte Qualitätsunternehmen mit starkem Burggraben, stabilen Cashflows und verlässlicher Historie (nach Beate Sander).
    * **✨ Geschliffener Diamant mit Zukunfts-Turbo:** Unternehmen, die solide Fundamentaldaten mit exponentiellem Wachstumspotenzial in Zukunftsbranchen (KI, Biotech, Cloud) verbinden (Schnittmenge Sander & Kurzweil).
    * **⛏️ Rohdiamant:** Junge oder stark schwankende Werte mit hoher Zukunftsvision, bei denen Forschung, Capex und Risiken noch genau abgewogen werden müssen.
    * **🚨 Hype-Ruine / Blender:** Unternehmen ohne echtes Produkt oder Fundament, die nur durch Marketing, leere Versprechungen oder betrügerische Guidance auffallen (Faktencheck gegen Blasen wie Nikola oder Theranos).
    """)
