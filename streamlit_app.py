import streamlit as st
import yfinance as yf
import math

st.set_page_config(
    page_title="OmaKurz Scanner v1.0",
    page_icon="🧭",
    layout="wide"
)

# --- STYLING ---
st.markdown("""
<style>
.main-header { text-align: center; padding: 10px 0; }
.main-header .compass { font-size: 64px; }
.main-header h1 { font-family: 'Georgia', serif; font-size: 36px; margin: 0; color: #1e293b; }
.main-header p { color: #64748b; font-size: 16px; margin-top: 5px; }
.quote { font-family: 'Georgia', serif; font-style: italic; font-size: 16px; color: #d97706; text-align: center; margin-bottom: 25px; }
.hammer-box { background-color: #fef2f2; border-left: 6px solid #dc2626; padding: 15px; border-radius: 4px; margin: 10px 0; }
.diamond-box { background-color: #f0fdf4; border-left: 6px solid #16a34a; padding: 15px; border-radius: 4px; margin: 10px 0; }
.fomo-shield { background-color: #fffbeb; border: 1px solid #fef3c7; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="main-header">
  <div class="compass">🧭</div>
  <h1>OMAKURZ™ SCANNER v1.0</h1>
  <p>Analyse-Kompass & Anti-FOMO Forensik</p>
</div>
<div class="quote">„Was du nicht verstehst oder was nicht belegt ist, kaufst du nicht.“</div>
""", unsafe_allow_html=True)

# --- SIDEBAR: FORENSIK & STORY CHECK (Qualitative Daten) ---
st.sidebar.header("🔬 Forensik-Labor (Manuelle Belege)")
st.sidebar.info("Hier prüfst du Angaben, die nicht in Standard-Bilanzen stehen (Wandelanleihen, Story, Pipeline).")

dilution_risk = st.sidebar.select_slider(
    "💰 Verwässerungs- & Wandelanleihen-Risiko",
    options=["Kein / Sehr niedrig", "Moderat (Optionen/Gering)", "Hoch (Wandelanleihen/Keine Belege)", "Akut (Ständige Kapitalerhöhung)"],
    value="Kein / Sehr niedrig"
)

story_gap = st.sidebar.select_slider(
    "🧠 Story vs. Reality Gap",
    options=["Faktenbelegt & Transparent", "Leichte Versprechen ohne Beleg", "Hohe Diskrepanz / Hype", "Keine Belege / Transparenzwarnung"],
    value="Faktenbelegt & Transparent"
)

pipeline_stage = st.sidebar.selectbox(
    "🧬 Pipeline / Tech-Entwicklung",
    ["Keine Pipeline (Klassisches Business)", "Frühe Phase / Forschung (High Risk)", "Späte Phase / Meilensteine nah", "Kommerzialisiert & Skalierend"]
)

data_confidence = st.sidebar.slider("🔍 Daten-Vollständigkeit & Quellenqualität (%)", 10, 100, 90)

# --- MAIN INPUT ---
col_in1, col_in2 = st.columns([3, 1])
with col_in1:
    ticker_input = st.text_input("Börsenkürzel / Ticker eingeben (z.B. AAPL, NVDA, BNTX, 6501.T) ...", key="ticker")
with col_in2:
    st.write(" ")
    st.write(" ")
    scan_btn = st.button("🧭 Analyse starten", use_container_width=True)

if scan_btn or ticker_input:
    if not ticker_input:
        st.warning("Bitte gib ein gültiges Ticker-Symbol ein.")
    else:
        try:
            stock = yf.Ticker(ticker_input.strip().upper())
            info = stock.info

            # === DATEN-EXTRAKTION ===
            company_name = info.get("longName", ticker_input.upper())
            sector = info.get("sector", "Unbekannt")
            currency = info.get("currency", "USD")
            market_cap = info.get("marketCap", 0) or 0
            enterprise_value = info.get("enterpriseValue", 0) or 0
            shares_outstanding = info.get("sharesOutstanding", 0) or 0
            current_price = info.get("currentPrice", 0) or info.get("regularMarketPrice", 0) or 0

            # 1. Oma - Substanz
            total_cash = info.get("totalCash", 0) or 0
            total_debt = info.get("totalDebt", 0) or 0
            net_cash = total_cash - total_debt
            pe_ratio = info.get("trailingPE", None) or info.get("forwardPE", None)
            pb_ratio = info.get("priceToBook", None)
            payout_ratio = (info.get("payoutRatio", 0) or 0) * 100
            raw_div = info.get("dividendYield", 0) or 0
            div_yield = raw_div if raw_div > 0.15 else raw_div * 100

            # 2. Kurz - Zukunft & Cashflow
            op_cashflow = info.get("operatingCashflow", 0) or 0
            free_cashflow = info.get("freeCashflow", 0) or 0
            profit_margin = (info.get("profitMargins", 0) or 0) * 100
            rev_growth = (info.get("revenueGrowth", 0) or 0) * 100
            inst_ownership = (info.get("heldPercentInstitutions", 0) or 0) * 100

            # Runway Berechnung (bei Cash-Burn)
            runway_months = None
            if op_cashflow < 0 and total_cash > 0:
                annual_burn = abs(op_cashflow)
                runway_months = round((total_cash / annual_burn) * 12, 1)

            # Acceleration (Verdopplungszeit der Erlöse nach Rule of 72)
            doubling_years = round(72 / rev_growth, 1) if rev_growth > 0 else "N/A"

            # === OMA-HAMMER (Knockout-Risiken) ===
            hammer_triggers = []
            if op_cashflow < 0 and (runway_months is not None and runway_months < 12):
                hammer_triggers.append(f"🚨 **Akuter Cash-Burn:** Runway beträgt weniger als 12 Monate ({runway_months} Monate)! Insolvenz- oder Massenverwässerungsgefahr.")
            if dilution_risk in ["Hoch (Wandelanleihen/Keine Belege)", "Akut (Ständige Kapitalerhöhung)"]:
                hammer_triggers.append("🚨 **Verwässerungs-Falle:** Hohes Risiko von Wandelanleihen oder aggressiven Kapitalerhöhungen.")
            if story_gap in ["Hohe Diskrepanz / Hype", "Keine Belege / Transparenzwarnung"]:
                hammer_triggers.append("🚨 **Story-Reality Gap:** Das Management verspricht mehr, als Bilanzen und Fakten belegen können.")
            if data_confidence < 40:
                hammer_triggers.append("🔍 **Nicht ausreichend verstanden:** Die Datenlage ist zu unvollständig für ein solides Urteil.")

            # === SCORE BERECHNUNG ===
            # Oma-Substanz Score
            oma_score = 50
            if net_cash > 0: oma_score += 25
            else: oma_score -= 20
            if pb_ratio and pb_ratio < 3.0: oma_score += 15
            if payout_ratio > 0 and payout_ratio <= 70: oma_score += 10
            elif payout_ratio > 90: oma_score -= 20
            oma_score = max(0, min(100, oma_score))

            # Kurz-Zukunft Score
            kurz_score = 50
            if rev_growth > 10: kurz_score += 20
            elif rev_growth < 0: kurz_score -= 20
            if profit_margin > 15: kurz_score += 15
            if inst_ownership > 50: kurz_score += 15
            kurz_score = max(0, min(100, kurz_score))

            # DIAMANTEN-STATUS
            if hammer_triggers:
                status_class = "🔨 OMA-HAMMER"
                status_desc = "Kritische Warnsignale aktiv. Kein Investment ohne vollständige Klärung der Belege!"
            elif oma_score >= 75 and kurz_score >= 75 and data_confidence >= 80:
                status_class = "💎 Kronjuwel / Geschliffener Diamant"
                status_desc = "Höchste Substanz, starker operativer Cashflow und exzellente Datenbelege."
            elif oma_score >= 60 and kurz_score >= 60:
                status_class = "💠 Rohdiamant"
                status_desc = "Gute Substanz mit Potenzial. Einzelne Parameter noch zu beobachten."
            elif oma_score >= 50:
                status_class = "🪨 Rohstein"
                status_desc = "Durchschnittliches Unternehmen oder Mischkonzern mit Einschränkungen."
            else:
                status_class = "⚠️ Spekulativer Fall"
                status_desc = "Erhöhte Risiken in Bilanz oder Finanzierung."

            # === AUSGABE HEADER ===
            st.markdown(f"## Ergebnisse für **{company_name}** ({sector})")
            
            # Anti-FOMO Schild
            st.markdown(f"""
            <div class="fomo-shield">
              <strong>🛡️ OmaKurz™ Anti-FOMO Schild:</strong><br>
              Lass dich nicht von Narrativen leiten. 
              <strong>Marktkapitalisierung:</strong> {market_cap / 1e9:.2f} Mrd. {currency} | 
              <strong>Enterprise Value (EV):</strong> {enterprise_value / 1e9:.2f} Mrd. {currency} | 
              <strong>Daten-Vertrauen:</strong> {data_confidence} %
            </div>
            """, unsafe_allow_html=True)

            # STATUS / DIAMANT
            if "OMA-HAMMER" in status_class:
                st.markdown(f"""
                <div class="hammer-box">
                  <h3 style="margin:0; color:#dc2626;">🔨 STATUS: OMA-HAMMER AKTIV</h3>
                  <p style="margin:5px 0 0 0; color:#991b1b;">{status_desc}</p>
                </div>
                """, unsafe_allow_html=True)
                for ht in hammer_triggers:
                    st.error(ht)
            else:
                st.markdown(f"""
                <div class="diamond-box">
                  <h3 style="margin:0; color:#16a34a;">STATUS: {status_class}</h3>
                  <p style="margin:5px 0 0 0; color:#166534;">{status_desc}</p>
                </div>
                """, unsafe_allow_html=True)

            st.divider()

            # --- Säulen & Scores ---
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("🏛️ Oma - Substanz", f"{oma_score} / 100")
            s2.metric("🚀 Kurz - Zukunft", f"{kurz_score} / 100")
            s3.metric("⚡ Dynamic / Growth", f"{rev_growth:.1f} % p.a.")
            s4.metric("🔍 Belege & Transparenz", f"{data_confidence} %")

            st.divider()

            # TAB-STRUKTUR FÜR DETAILS
            tab1, tab2, tab3, tab4 = st.columns(4)

            # TAB 1: SUBSTANZ & FINANZ-DETEKTIV
            st.subheader("🕵️‍♂️ 1. Finanzierungs-Detektiv & Substanz")
            f1, f2, f3, f4 = st.columns(4)
            f1.metric("Netto-Cash", f"{net_cash / 1e9:.2f} Mrd. {currency}", delta="Positiv" if net_cash > 0 else "Verschuldet")
            f2.metric("Operativer Cashflow", f"{op_cashflow / 1e9:.2f} Mrd. {currency}")
            
            if op_cashflow > 0:
                f3.metric("Finanzierung", "✅ Aus Betrieb")
            else:
                f3.metric("Finanzierung", "🚨 Cash Burn")
                
            f4.metric("Runway (Reichweite)", f"{runway_months} Monate" if runway_months else "Unbegrenzt (Cashflow +)")

            # TAB 2: ACCELERATION & VALUATION
            st.subheader("⚖️ 2. Acceleration, Penny-Stock-Check & Valuation")
            v1, v2, v3, v4 = st.columns(4)
            v1.metric("KGV", f"{pe_ratio:.1f}" if pe_ratio else "k.A.")
            v2.metric("KBV (Buchwert)", f"{pb_ratio:.2f}" if pb_ratio else "k.A.")
            v3.metric("Erlös-Verdopplung", f"~ {doubling_years} Jahre" if isinstance(doubling_years, (int, float)) else "Kein Wachstum")
            v4.metric("Aktienanzahl", f"{shares_outstanding / 1e6:.1f} Mio.")

            # Reverse Valuation Denkmodell
            with st.expander("🔮 Reverse Valuation: Was ist im Preis eingepreist?"):
                st.write(f"""
                Um den aktuellen Aktienkurs von **{current_price} {currency}** zu rechtfertigen:
                * Müsste das Unternehmen seinen Gewinnmarge-Standard von **{profit_margin:.1f} %** halten oder ausbauen.
                * Muss das Wachstum von derzeit **{rev_growth:.1f} %** dauerhaft gehalten werden.
                * Ist ein Enterprise Value von **{enterprise_value / 1e9:.2f} Mrd. {currency}** am Markt angesetzt.
                """)

            # TAB 3: STORY VS. REALITY & PIPELINE
            st.subheader("🧬 3. Pipeline, Story & Governance")
            p1, p2, p3 = st.columns(3)
            p1.metric("Pipeline-Status", pipeline_stage)
            p2.metric("Story vs. Reality", story_gap)
            p3.metric("Verwässerungs-Risiko", dilution_risk)

            # TAB 4: ENTWICKLUNGSKORRIDOR
            st.subheader("🔮 4. Entwicklungskorridor (Szenarien ohne Kristallkugel)")
            c1, c2, c3 = st.columns(3)
            c1.warning(f"**Konservativ:** Flaches Wachstum, Margendruck. Fokus auf Netto-Cash ({net_cash / 1e9:.1f} Mrd. {currency}).")
            c2.info(f"**Basis-Pfad:** Fortführung des aktuellen Trends ({rev_growth:.1f} % Wachstum, {profit_margin:.1f} % Marge).")
            c3.success(f"**Beschleunigt:** Kommerzialisierung gelingt, Erlöse verdoppeln sich alle {doubling_years} Jahre.")

        except Exception as e:
            st.error(f"Fehler beim Abrufen oder Verarbeiten der Daten: {e}")

st.divider()
st.caption("OmaKurz™ Scanner v1.0 · Anti-FOMO Analyse-System · Keine Anlageberatung")
            
