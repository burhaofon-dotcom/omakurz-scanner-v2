import streamlit as st
import yfinance as yf
import google.generativeai as genai
import pandas as pd

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="Oma-Kurz-Kompass ULTRA v2",
    page_icon="💎",
    layout="wide"
)

# --- SICHERE API-KEY INITIALISIERUNG (Backend / st.secrets) ---
# Der Key wird sicher über Streamlit Secrets geladen (keinsefalls im Frontend-Code sichtbar!)
# In deiner lokalen .streamlit/secrets.toml hinterlegst du: GEMINI_API_KEY = "dein_schlüssel"
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("Sicherheitsfehler: Kein Gemini API-Key in den Streamlit-Secrets gefunden! Bitte hinterlege den Key in der Konfiguration.")
    st.stop()

# --- MODELL AUSWAHL ---
generation_config = {
    "temperature": 0.3,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",  # stabiles High-Performance Modell
    generation_config=generation_config
)

# --- SEITEN-LAYOUT & STYLING ---
st.title("💎 Oma-Kurz-Kompass ULTRA v2")
st.markdown("Der globale Bilanz- und Zukunfts-Stresstest für Aktien nach Beate Sander & Ray Kurzweil – robust, transparent & plausibel.")

# --- SIDEBAR: GLOSSAR / BÖRSEN-LEXIKON ---
with st.sidebar:
    st.header("📖 Börsen-Glossar & Hilfe")
    st.markdown("Damit auch Einsteiger im Familienkreis sofort durchsteigen, hier die wichtigsten Kennzahlen im Überblick:")
    
    with st.expander("Was ist das KGV?"):
        st.write("**Kurs-Gewinn-Verhältnis (P/E Ratio):** Zeigt, wie teuer ein Unternehmen bezogen auf seinen Gewinn ist. Ein KGV unter 15 gilt oft als günstig, über 25 als wachstumsstark oder teuer.")
        
    with st.expander("Was bedeutet Schuldenquote (D/E)?"):
        st.write("**Debt-to-Equity (Verschuldungsgrad):** Verhältnis von Schulden zu Eigenkapital. Nach Beate Sander max. 25–50% bei Industrieunternehmen. Bei Banken & BDCs (wie Main Street Capital) sind höhere Hebel strukturell bedingt normal.")
        
    with st.expander("Was ist die Payout Ratio?"):
        st.write("**Ausschüttungsquote:** Welcher Prozentsatz des Gewinns als Dividende ausgezahlt wird. 40–60% gelten als gesund, Werte nahe 0% oder über 100% erfordern Prüfung.")

    with st.expander("Die Härtegrade erklärt"):
        st.write("""
        - **💎 Geschliffener Brillant:** Top-Unternehmen mit starker Substanz und Zukunftstrend.
        - **🧱 Unpolierter Rohstein:** Solide Substanz, aber temporäre Belastungen, Schulden oder Restrukturierung.
        - **⚠️ Dividenden-Falle / Niete:** Hohes Pleiterisiko, toxische Verschuldung oder substanzloser Verfall.
        """)
    
    st.divider()
    st.markdown("🔒 *Sicherer Modus: API-Key zentral im Backend gekapselt.*")

# --- HAUPTEINGABE ---
ticker_input = st.text_input("Gib das Tickersymbol ein (z.B. `SU.PA`, `4768.T`, `MAIN`, `RKT.L`, `WHLR`):", value="SU.PA")

if st.button("ULTRA-Stresstest starten 🚀"):
    if not ticker_input:
        st.warning("Bitte gib ein gültiges Tickersymbol ein.")
    else:
        with st.spinner(f"Analysiere {ticker_input.upper()} im ULTRA v2 Modus..."):
            try:
                # Daten über yfinance abrufen
                stock = yf.Ticker(ticker_input)
                info = stock.info
                
                name = info.get('longName', ticker_input.upper())
                price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                currency = info.get('currency', 'EUR')
                pe_ratio = info.get('trailingPE', 0)
                if not pe_ratio or pe_ratio < 0:
                    pe_ratio = info.get('forwardPE', 0)
                
                # Schuldenquote berechnen / abgreifen
                debt_to_equity = info.get('debtToEquity', 0)
                if debt_to_equity and debt_to_equity > 10: 
                    # yfinance liefert D/E manchmal in Prozent (z.B. 84.1 statt 0.84)
                    de_display = debt_to_equity
                else:
                    de_display = debt_to_equity * 100 if debt_to_equity else 0
                
                payout_ratio = info.get('payoutRatio', 0)
                payout_display = payout_ratio * 100 if payout_ratio else 0.0

                # --- ANZEIGE DER GRUDDATEN ---
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Kurs", f"{price:.2f} {currency}")
                col2.metric("KGV", f"{pe_ratio:.2f}" if pe_ratio else "N/A")
                col3.metric("Schuldenquote (D/E)", f"{de_display:.2f}%")
                col4.metric("Payout Ratio", f"{payout_display:.1f}%")

                # --- PROMPT-STRUKTUR FÜR KI-ANALYSE MIT SEKTOR-KENNZEICHNUNG ---
                prompt = f"""
                Du bist der Senior-Stresstest-Analyst des 'Oma-Kurz-Kompass ULTRA v2' (Kombination aus Beate Sanders Substanz-Lehre und Ray Kurzweils Zukunfts-Accelerator).
                Analysiere das folgende Unternehmen anhand der Rohdaten und ermittle Sektor, Branche und Score:
                
                Unternehmensname: {name}
                Ticker: {ticker_input.upper()}
                KGV: {pe_ratio}
                Schuldenquote (D/E): {de_display}%
                Ausschüttungsquote: {payout_display}%
                
                Deine Aufgabe:
                1. Identifiziere exakt den Sektor und die Branche (z.B. Konsumgüter, Finanz-BDC, Industrie, Halbleiter, Software). Berücksichtige branchenspezifische Besonderheiten (z. B. hoher Hebel bei BDCs normal, strenge Industrie-Leine bei klassischen Firmen).
                2. Bestimme den Härtegrad genau aus diesen drei Kategorien: 
                   - "Geschliffener Brillant"
                   - "Unpolierter Rohstein"
                   - "Dividenden-Falle" (oder Pleite-Bude bei extremen Werten).
                3. Vergib einen dynamischen ULTRA KI-Score von 1 bis 100 Punkten.
                4. Schreibe eine knackige, fundierte Analyse im Stil von Beate Sander & Ray Kurzweil (Bilanz-Stresstest + Zukunfts-Accelerator & Marktsituation).
                
                Antworte im folgenden exakten Markdown-Format:
                **Sektor & Branche:** [Dein erfaßter Sektor / Branche einfügen]
                **Härtegrad:** [Genauer Härtegrad]
                **Globaler Bilanz- & Schulden-Stresstest:** [Text...]
                **Der Zukunfts-Accelerator & Marktsituation:** [Text...]
                **Dynamischer ULTRA KI-Score:** [X] / 100
                """

                response = model.generate_content(prompt)
                analysis_text = response.text

                # --- ERGEBNIS-AUSGABE ---
                st.markdown("---")
                st.markdown(analysis_text)
                
                st.success("Stresstest erfolgreich im sicheren Backend-Modus durchgeführt!")

            except Exception as e:
                st.error(f"Fehler bei der Datenabfrage oder Analyse: {e}")
