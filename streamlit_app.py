# ==========================================
# OmaKurz™ Kompass - Hauptanwendung (streamlit_app.py)
# Komplettpaket mit KGV-Fallback und neuen Sparten (Lebensmittel, Chemie)
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
        ticker_input = st.text_input("Ticker-Symbol eingeben (z. B. HMC, 7267.T, RECKITT.L, 4063.T):", value="7267.T").upper()
    with col_input2:
        st.write("") 
        st.write("")
        analysis_triggered = st.button("🚀 Analysieren", use_container_width=True)

    if analysis_triggered and ticker_input:
        with st.spinner(f"Berechne das 10-Säulen-Modell für {ticker_input}..."):
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
                        pass 
                
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
                    is_reit = "REIT" in industry or "Real Estate" in sector
                    is_bdc = "Capital" in name or "Investment" in industry or "Credit" in industry or ticker_input == "MAIN"
                    is_semis = "Semiconductor" in industry or "Semiconductors" in sector or "Electronics" in industry
                    is_tech = sector in ["Technology", "Communication Services"] and not is_semis
                    is_auto_mobility = sector in ["Consumer Cyclical", "Automotive"] or "Auto" in industry or "Vehicle" in industry
                    
                    # --- NEUE SPATEN ---
                    is_food_consumer = sector in ["Consumer Defensive"] or "Household" in industry or "Food" in industry or "Beverages" in industry
                    is_chem_materials = sector in ["Basic Materials", "Chemicals"] or "Chemical" in industry or "Specialty Chemicals" in industry
                    is_industrial = sector in ["Industrials", "Manufacturing"] and not is_chem_materials
                    
                    # Effektives KGV mit Fallback falls Yahoo Finance "N/A" liefert
                    effective_pe = pe_ratio if (pe_ratio and pe_ratio > 0) else 15.0 
                    effective_margin = profit_margins if profit_margins else 0.08 # solider Default-Annahme-Wert bei Datenlücken

                    # --- 1. SANDER-LOGIK ---
                    if is_reit or is_bdc:
                        sander_kgv = 4 
                        sander_marge = 4 if effective_margin > 0.15 else 3
                    elif is_semis or is_tech:
                        sander_kgv = 5 if effective_pe < 40 else 3
                        sander_marge = 5 if effective_margin > 0.20 else 3
                    elif is_auto_mobility:
                        sander_kgv = 5 if effective_pe < 18 else 3
                        sander_marge = 4 if effective_margin > 0.03 else 3
                    elif is_food_consumer: # Neu: Lebensmittel & Haushaltsgüter (stabil, defensiv)
                        sander_kgv = 5 if effective_pe < 22 else 3
                        sander_marge = 5 if effective_margin > 0.10 else 3
                    elif is_chem_materials: # Neu: Chemie & Spezialmaterialien
                        sander_kgv = 5 if effective_pe < 20 else 3
                        sander_marge = 4 if effective_margin > 0.08 else 3
                    else:
                        sander_kgv = 5 if effective_pe < 22 else 3
                        sander_marge = 5 if effective_margin > 0.10 else 3
                        
                    sander_burggraben = 5 if ticker_input in ["SONY", "SAP", "MSFT", "AAPL", "8306.T", "8035.T", "HMC", "7267.T", "RECKITT.L", "O", "NEE", "MAIN", "4063.T"] else 3
                    sander_cashflow = 5 if (is_reit or is_bdc or is_food_consumer) else (4 if effective_margin > 0.06 else 2)
                    sander_bilanz = 4 
                    
                    summe_sander = sander_marge + sander_kgv + sander_burggraben + sander_cashflow + sander_bilanz
                    sander_punkte = summe_sander * 2 
                    
                    # --- 2. KURZWEIL-LOGIK ---
                    if is_semis:
                        k_sektor, k_skalierung, k_loesung = 5, 5, 5 
                    elif is_tech:
                        k_sektor, k_skalierung, k_loesung = 5, 5, 4
                    elif is_auto_mobility:
                        k_sektor, k_skalierung, k_loesung = 4, 4, 4
                    elif is_chem_materials: # Chemie treibt oft Nanotech, Materialien & Future Tech
                        k_sektor, k_skalierung, k_loesung = 4, 4, 4
                    elif is_food_consumer: # Defensiver Konsum: stabiles Rückgrat, moderat in exponentieller Tech
                        k_sektor, k_skalierung, k_loesung = 3, 3, 3
                    elif is_industrial:
                        k_sektor, k_skalierung, k_loesung = 4, 4, 4 
                    elif is_reit or is_bdc or sector in ["Energy", "Utilities", "Financial Services"]:
                        k_sektor, k_skalierung, k_loesung = 3, 3, 3 
                    elif sector in ["Healthcare"]:
                        k_sektor, k_skalierung, k_loesung = 5, 3, 4
                    else:
                        k_sektor, k_skalierung, k_loesung = 3, 3, 3
                    
                    kurzweil_innovation = 4 if (is_auto_mobility or is_chem_materials) else (5 if is_semis else 3)
                    kurzweil_jobs_markt = 4
                    
                    summe_kurzweil = k_sektor + k_skalierung + k_loesung + kurzweil_innovation + kurzweil_jobs_markt
                    kurzweil_punkte = summe_kurzweil * 2 
                    
                    gesamt_punkte = min(98, sander_punkte + kurzweil_punkte)
                    
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
                elif is_auto_mobility:
                    status = "🚗 Solider Mobilitäts- & Value-Anker (Mit Innovations-Turbo)"
                    ausblick = "Klassischer Automobil- und Motorenbauer mit starken Marken, globaler Substanz und konsequenter Transformation."
                elif is_food_consumer:
                    status = "🛒 Defensiver Konsum- & Marken-Anker (Krisenfest)"
                    ausblick = "Verlässlicher Konsumgüter-Riese mit starken Cashflows und hoher Preissetzungsmacht."
                elif is_chem_materials:
                    status = "🧪 Industrieller Chemie- & Material-Spezialist"
                    ausblick = "Unverzichtbarer Grundstoff- und Spezialchemie-Player für globale Lieferketten."
                elif is_semis:
                    status = "⚡ High-Tech Chip-Kraftwerk & Exponentieller Infrastruktur-Spaten"
                    ausblick = "Hervorragender Halbleiter-Ausrüster oder Chip-Player."
                elif is_bdc:
                    status = "💰 Hochprozentiger BDC-Zins- & Dividenden-Anker"
                    ausblick = "Starker BDC mit hohen Ausschüttungen."
                elif is_reit:
                    status = "🏢 Solider Immobilien-Cashflow-Anker"
                    ausblick = "Hervorragender REIT für verlässliche Cashflows."
                elif gesamt_punkte >= 85:
                    status = "💎 Omas absolut unangetastetes Kronjuwel"
                    ausblick = "Hervorragende Symbiose aus starker Substanz und Zukunfts-Turbo."
                else:
                    status = "✨ Solider Wert mit gutem Potenzial"
                    ausblick = "Ordentliches Fundament im gewählten Spaten."
                    
                st.info(f"**Klassifizierung:** {status}\n\n**36-Monats-Fokus:** {ausblick}")
                
                watch_label = f"{name} ({ticker_input}) - {gesamt_punkte}/100 Pkt"
                if st.button("📌 Zur Watchlist hinzufügen"):
                    if watch_label not in st.session_state.watchlist:
                        st.session_state.watchlist.append(watch_label)
                        st.success("Erfolgreich zur Watchlist hinzugefügt! (Siehe Sidebar links)")
                        st.rerun()
                    else:
                        st.warning("Bereits auf der Watchlist.")
                
            except Exception as e:
                st.error(f"Fehler beim Abrufen der Daten für {ticker_input}: {e}")

else:
    st.markdown("### 🦄 Pre-IPO / Private Unicorn Web-Faktenchecker")
    # (Unicorn-Logik)
