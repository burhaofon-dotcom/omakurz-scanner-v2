from typing import Optional

import numpy as np
import pandas as pd

from omakurz_helpers import (
    safe_float,
    clean_series,
    latest_value,
    percent_change,
    get_last_two_values,
    get_last_three_values,
)
def classify_acceleration(
    growth_series: Optional[pd.Series],
) -> dict:
    """
    Bewertet, ob sich das Wachstum beschleunigt,
    stabil bleibt oder verlangsamt.
    """

    series = clean_series(growth_series)

    if len(series) < 2:
        return {
            "status": "⚪ Keine ausreichenden Daten",
            "acceleration": None,
            "reason": "Für eine Beschleunigungsanalyse fehlen historische Wachstumswerte.",
        }

    current_growth = safe_float(series.iloc[-1])
    previous_growth = safe_float(series.iloc[-2])

    if current_growth is None or previous_growth is None:
        return {
            "status": "⚪ Keine ausreichenden Daten",
            "acceleration": None,
            "reason": "Die vorhandenen Wachstumswerte konnten nicht sauber ausgewertet werden.",
        }

    acceleration = current_growth - previous_growth

    if acceleration > 2.0:
        status = "🟢 Beschleunigung"
    elif acceleration < -2.0:
        status = "🔴 Wachstumsverlangsamung"
    else:
        status = "🟡 Wachstum, aber keine klare Beschleunigung"

    return {
        "status": status,
        "acceleration": acceleration,
        "current_growth": current_growth,
        "previous_growth": previous_growth,
        "reason": (
            "Die Beschleunigung wird als Veränderung der Wachstumsrate "
            "in Prozentpunkten bewertet."
        ),
    }
  def calculate_margin_series(
    revenue_series: Optional[pd.Series],
    net_income_series: Optional[pd.Series],
) -> pd.Series:
    """
    Berechnet die Nettomarge als Prozent des Umsatzes.
    """

    revenue = clean_series(revenue_series)
    net_income = clean_series(net_income_series)

    if revenue.empty or net_income.empty:
        return pd.Series(dtype=float)

    combined = pd.concat(
        [revenue.rename("revenue"), net_income.rename("net_income")],
        axis=1,
    ).dropna()

    if combined.empty:
        return pd.Series(dtype=float)

    combined = combined[combined["revenue"] != 0]

    if combined.empty:
        return pd.Series(dtype=float)

    margin = (
        combined["net_income"]
        / combined["revenue"]
        * 100.0
    )

    return margin.dropna()
  def classify_margin_trend(
    margin_series: Optional[pd.Series],
) -> dict:
    """
    Bewertet die Entwicklung der Nettomarge.
    """

    series = clean_series(margin_series)

    if len(series) < 2:
        return {
            "status": "⚪ Keine ausreichenden Daten",
            "change": None,
            "reason": "Für die Margenentwicklung fehlen historische Werte.",
        }

    current_margin = safe_float(series.iloc[-1])
    previous_margin = safe_float(series.iloc[-2])

    if current_margin is None or previous_margin is None:
        return {
            "status": "⚪ Keine ausreichenden Daten",
            "change": None,
            "reason": "Die vorhandenen Margenwerte konnten nicht sauber ausgewertet werden.",
        }

    change = current_margin - previous_margin

    if change > 1.0:
        status = "🟢 Margen verbessern sich"
    elif change < -1.0:
        status = "🔴 Margen verschlechtern sich"
    else:
        status = "🟡 Margen weitgehend stabil"

    return {
        "status": status,
        "change": change,
        "current_margin": current_margin,
        "previous_margin": previous_margin,
        "reason": (
            "Bewertet wird die Veränderung der Nettomarge "
            "in Prozentpunkten."
        ),
    }
  def classify_fcf_dynamics(
    fcf_series: Optional[pd.Series],
) -> dict:
    """
    Bewertet die Entwicklung des Free Cash Flow.
    """

    series = clean_series(fcf_series)

    if len(series) < 2:
        return {
            "status": "⚪ Keine ausreichenden Daten",
            "change": None,
            "reason": "Für die FCF-Dynamik fehlen historische Werte.",
        }

    current_fcf = safe_float(series.iloc[-1])
    previous_fcf = safe_float(series.iloc[-2])

    if current_fcf is None or previous_fcf is None:
        return {
            "status": "⚪ Keine ausreichenden Daten",
            "change": None,
            "reason": "Die vorhandenen FCF-Werte konnten nicht sauber ausgewertet werden.",
        }

    change = current_fcf - previous_fcf

    if current_fcf > 0 and previous_fcf <= 0:
        status = "🟢 FCF dreht ins Positive"
    elif current_fcf > previous_fcf:
        status = "🟢 FCF verbessert sich"
    elif current_fcf < previous_fcf:
        status = "🔴 FCF verschlechtert sich"
    else:
        status = "🟡 FCF weitgehend unverändert"

    return {
        "status": status,
        "change": change,
        "current_fcf": current_fcf,
        "previous_fcf": previous_fcf,
        "reason": (
            "Die FCF-Dynamik zeigt die Veränderung des Free Cash Flow. "
            "Eine Verbesserung des FCF ist nicht automatisch eine echte "
            "Beschleunigung des operativen Geschäfts."
        ),
    }

def analyze_dilution(
    share_series: Optional[pd.Series],
) -> dict:
    """
    Bewertet die Entwicklung der Aktienzahl.

    Eine steigende Aktienzahl wird nicht automatisch als
    bewiesene Verwässerung interpretiert.
    """

    series = clean_series(share_series)

    if len(series) < 2:
        return {
            "status": "⚪ Keine ausreichenden Daten",
            "change_percent": None,
            "reason": (
                "Für die Entwicklung der Aktienzahl fehlen "
                "historische Werte."
            ),
        }

    current_shares = safe_float(series.iloc[-1])
    previous_shares = safe_float(series.iloc[-2])

    if current_shares is None or previous_shares is None:
        return {
            "status": "⚪ Keine ausreichenden Daten",
            "change_percent": None,
            "reason": "Die Aktienzahl konnte nicht sauber ausgewertet werden.",
        }

    if previous_shares == 0:
        return {
            "status": "⚪ Nicht bewertbar",
            "change_percent": None,
            "reason": "Der Vergleichswert der Aktienzahl ist null.",
        }

    change_percent = (
        (current_shares - previous_shares)
        / abs(previous_shares)
        * 100.0
    )

    if change_percent > 5.0:
        status = (
            "🔴 Deutlicher Anstieg der Aktienzahl — "
            "Finanzierung/Equity-Komponenten prüfen"
        )
    elif change_percent > 1.0:
        status = "🟡 Aktienzahl gestiegen — Ursache ungeklärt"
    else:
        status = "🟢 Aktienzahl stabil/nahezu stabil"

    return {
        "status": status,
        "change_percent": change_percent,
        "current_shares": current_shares,
        "previous_shares": previous_shares,
        "reason": (
            "Eine steigende Aktienzahl kann unter anderem durch "
            "Kapitalerhöhungen, Stock Compensation, Akquisitionen, "
            "Optionen/RSUs, Convertibles oder Änderungen der "
            "Berichterstattung entstehen. Die Ursache muss separat "
            "geprüft werden."
        ),
    }
  def calculate_runway_years(
    cash: Optional[float],
    fcf_series: Optional[pd.Series],
) -> Optional[float]:
    """
    Schätzt einen einfachen Cash-Runway anhand negativer FCF-Werte.

    Das ist nur eine Näherung und keine belastbare Liquiditätsprognose.
    """

    cash_value = safe_float(cash)
    series = clean_series(fcf_series)

    if cash_value is None or cash_value <= 0 or series.empty:
        return None

    negative_values = series[series < 0]

    if negative_values.empty:
        return None

    average_burn = abs(float(negative_values.mean()))

    if average_burn <= 0:
        return None

    return cash_value / average_burn


def analyze_financing(
    cash: Optional[float],
    debt: Optional[float],
    net_cash: Optional[float],
    financing_cash_flow: Optional[float],
    fcf_series: Optional[pd.Series],
) -> dict:
    """
    Erstellt einen Finanzierungs-Check aus Liquidität,
    Verschuldung, FCF und Finanzierungscashflow.
    """

    cash_value = safe_float(cash)
    debt_value = safe_float(debt)
    net_cash_value = safe_float(net_cash)
    financing_cf = safe_float(financing_cash_flow)

    runway = calculate_runway_years(cash_value, fcf_series)

    warnings = []

    if debt_value is not None and cash_value is not None:
        if debt_value > cash_value:
            warnings.append(
                "Schulden liegen über der verfügbaren Liquidität."
            )

    if financing_cf is not None and financing_cf > 0:
        warnings.append(
            "Positiver Finanzierungscashflow: mögliche Kapitalaufnahme "
            "oder andere Finanzierungskomponenten prüfen."
        )

    if runway is not None and runway < 2:
        warnings.append(
            "Niedrige rechnerische FCF-Laufzeit — Liquidität und "
            "künftigen Finanzierungsbedarf genauer prüfen."
        )

    if not warnings:
        warnings.append(
            "Keine offensichtliche Finanzierungswarnung aus den "
            "verfügbaren Kennzahlen."
        )

    return {
        "cash": cash_value,
        "debt": debt_value,
        "net_cash": net_cash_value,
        "financing_cash_flow": financing_cf,
        "runway_years": runway,
        "warnings": warnings,
        "reason": (
            "Der Scanner unterstellt keinen bestimmten Grund für "
            "eine Kapitalaufnahme. Mögliche Gründe können "
            "Refinanzierung, Akquisitionen, Ausbau, Laufzeiten oder "
            "Kapitalstruktur sein."
        ),
    }
  def calculate_evidence(
    revenue_series: Optional[pd.Series],
    net_income_series: Optional[pd.Series],
    operating_cash_flow_series: Optional[pd.Series],
    fcf_series: Optional[pd.Series],
    cash_series: Optional[pd.Series],
    debt_series: Optional[pd.Series],
    share_series: Optional[pd.Series],
) -> dict:
    """
    Bewertet die Datenbasis des Scanners.

    Der Score beschreibt die verfügbare Datenqualität und
    nicht die Qualität des Unternehmens selbst.
    """

    series_list = [
        revenue_series,
        net_income_series,
        operating_cash_flow_series,
        fcf_series,
        cash_series,
        debt_series,
        share_series,
    ]

    available = 0
    total = len(series_list)
    history_points = 0
    missing = []

    names = [
        "Umsatz",
        "Nettoergebnis",
        "Operativer Cashflow",
        "Free Cash Flow",
        "Cash",
        "Schulden",
        "Aktienzahl",
    ]

    for name, series in zip(names, series_list):
        cleaned = clean_series(series)

        if len(cleaned) > 0:
            available += 1
            history_points += len(cleaned)
        else:
            missing.append(name)

    if total == 0:
        score = 0
    else:
        completeness = available / total
        score = round(completeness * 100)

    if score >= 85:
        label = "🟢 Hohe Datenabdeckung"
    elif score >= 60:
        label = "🟡 Mittlere Datenabdeckung"
    else:
        label = "🔴 Niedrige Datenabdeckung"

    notes = [
        "Der Evidenz-Score misst die verfügbare Datengrundlage, "
        "nicht automatisch die Qualität des Unternehmens.",
        "Historische Daten sollten möglichst über mehrere Perioden "
        "vorliegen, damit Trends belastbar bewertet werden können.",
        "Die Daten stammen aus einer sekundären Datenquelle und "
        "ersetzen keine Prüfung von Geschäftsberichten oder "
        "Primärquellen.",
    ]

    if missing:
        notes.append(
            "Fehlende Datenfelder: " + ", ".join(missing)
        )

    return {
        "score": score,
        "label": label,
        "available_fields": available,
        "total_fields": total,
        "history_points": history_points,
        "missing": missing,
        "notes": notes,
      }
  def build_oma_score(
    cash: Optional[float],
    debt: Optional[float],
    net_cash: Optional[float],
    operating_cash_flow_series: Optional[pd.Series],
    fcf_series: Optional[pd.Series],
    margin_series: Optional[pd.Series],
    dilution_analysis: Optional[dict],
    evidence_score: Optional[float],
) -> dict:
    """
    Erstellt einen heuristischen Oma-Score von 0 bis 100.

    Der Score bewertet finanzielle Substanz und Belastbarkeit,
    nicht die Attraktivität einer Aktie oder deren Bewertung.
    """

    score = 0.0
    reasons = []

    cash_value = safe_float(cash)
    debt_value = safe_float(debt)
    net_cash_value = safe_float(net_cash)
    evidence_value = safe_float(evidence_score)

    if cash_value is not None and cash_value > 0:
        score += 15
        reasons.append("Liquidität vorhanden")
    elif cash_value is not None:
        reasons.append("Keine starke positive Liquiditätsbasis")

    if net_cash_value is not None and net_cash_value > 0:
        score += 20
        reasons.append("Nettocash-Position positiv")
    elif net_cash_value is not None and net_cash_value < 0:
        score -= 10
        reasons.append("Nettoverschuldung vorhanden")

    if debt_value is not None and cash_value is not None:
        if cash_value > debt_value:
            score += 10
            reasons.append("Cash übersteigt ausgewiesene Schulden")
        elif debt_value > cash_value:
            reasons.append("Schulden übersteigen Cash")

    ocf = clean_series(operating_cash_flow_series)

    if not ocf.empty:
        latest_ocf = safe_float(ocf.iloc[-1])

        if latest_ocf is not None and latest_ocf > 0:
            score += 15
            reasons.append("Operativer Cashflow positiv")
        elif latest_ocf is not None:
            score -= 5
            reasons.append("Operativer Cashflow negativ")

    fcf = clean_series(fcf_series)

    if not fcf.empty:
        latest_fcf = safe_float(fcf.iloc[-1])

        if latest_fcf is not None and latest_fcf > 0:
            score += 15
            reasons.append("Free Cash Flow positiv")
        elif latest_fcf is not None:
            score -= 5
            reasons.append("Free Cash Flow negativ")

    margins = clean_series(margin_series)

    if not margins.empty:
        latest_margin = safe_float(margins.iloc[-1])

        if latest_margin is not None and latest_margin > 0:
            score += 10
            reasons.append("Nettomarge positiv")

    if dilution_analysis:
        dilution_change = safe_float(
            dilution_analysis.get("change_percent")
        )

        if dilution_change is not None:
            if dilution_change <= 1:
                score += 10
                reasons.append("Aktienzahl weitgehend stabil")
            elif dilution_change > 5:
                score -= 5
                reasons.append("Aktienzahl deutlich gestiegen")
            else:
                reasons.append("Aktienzahl moderat gestiegen")

    if evidence_value is not None:
        score += max(0.0, min(5.0, evidence_value / 20.0))

    score = max(0.0, min(100.0, round(score)))

    if score >= 80:
        label = "🟢 Oma stark"
    elif score >= 60:
        label = "🟡 Oma ordentlich"
    elif score >= 40:
        label = "🟠 Oma mit Fragezeichen"
    else:
        label = "🔴 Oma kritisch"

    return {
        "score": score,
        "label": label,
        "reasons": reasons,
        "note": (
            "Der Oma-Score ist ein heuristischer Scanner-Wert. "
            "Er ersetzt keine vollständige Bilanz-, Cashflow- "
            "oder Unternehmensanalyse."
        ),
  }
  def build_kurz_score(
    revenue_series: Optional[pd.Series],
    acceleration_analysis: Optional[dict],
    margin_analysis: Optional[dict],
    evidence_score: Optional[float],
) -> dict:
    """
    Erstellt einen heuristischen Kurz-Score von 0 bis 100.

    Bewertet Wachstum und Dynamik, nicht die Aktienbewertung.
    """

    score = 0.0
    reasons = []

    revenue = clean_series(revenue_series)

    if len(revenue) >= 2:
        current_revenue = safe_float(revenue.iloc[-1])
        previous_revenue = safe_float(revenue.iloc[-2])

        if (
            current_revenue is not None
            and previous_revenue is not None
            and previous_revenue != 0
        ):
            growth = (
                (current_revenue - previous_revenue)
                / abs(previous_revenue)
                * 100.0
            )

            if growth > 20:
                score += 25
                reasons.append("Starkes Umsatzwachstum")
            elif growth > 5:
                score += 15
                reasons.append("Positives Umsatzwachstum")
            elif growth > 0:
                score += 8
                reasons.append("Umsatz wächst leicht")
            else:
                reasons.append("Umsatz rückläufig")

    if acceleration_analysis:
        acceleration = safe_float(
            acceleration_analysis.get("acceleration")
        )

        if acceleration is not None:
            if acceleration > 2:
                score += 20
                reasons.append("Wachstum beschleunigt")
            elif acceleration < -2:
                score -= 5
                reasons.append("Wachstum verlangsamt")
            else:
                score += 5
                reasons.append("Wachstum ohne klare Beschleunigung")

    if margin_analysis:
        margin_change = safe_float(
            margin_analysis.get("change")
        )

        if margin_change is not None:
            if margin_change > 1:
                score += 15
                reasons.append("Margen verbessern sich")
            elif margin_change < -1:
                score -= 5
                reasons.append("Margen verschlechtern sich")
            else:
                score += 5
                reasons.append("Margen weitgehend stabil")

    if evidence_score is not None:
        score += max(
            0.0,
            min(10.0, safe_float(evidence_score) / 10.0),
        )

    score = max(0.0, min(100.0, round(score)))

    if score >= 80:
        label = "🟢 Kurz stark"
    elif score >= 60:
        label = "🟡 Kurz interessant"
    elif score >= 40:
        label = "🟠 Kurz mit Fragezeichen"
    else:
        label = "🔴 Kurz schwach"

    return {
        "score": score,
        "label": label,
        "reasons": reasons,
        "note": (
            "Der Kurz-Score bewertet Wachstum und Dynamik. "
            "Er ist kein Kursziel und keine Kaufempfehlung."
        ),
    }
  def build_core_judgment(
    oma_score: Optional[dict],
    kurz_score: Optional[dict],
) -> dict:
    """
    Verbindet Oma- und Kurz-Score zu einem qualitativen Gesamtbild.
    """

    oma = safe_float(
        oma_score.get("score")
        if oma_score
        else None
    )

    kurz = safe_float(
        kurz_score.get("score")
        if kurz_score
        else None
    )

    if oma is None or kurz is None:
        return {
            "status": "⚪ Gesamtbild nicht ausreichend bewertbar",
            "oma_score": oma,
            "kurz_score": kurz,
            "summary": (
                "Für ein Gesamtbild fehlen wichtige Bewertungsbausteine."
            ),
        }

    if oma >= 75 and kurz >= 75:
        status = "💎 Substanz stark + Zukunftsdynamik stark"
        summary = (
            "Die finanzielle Substanz und die beobachtbare "
            "Wachstumsdynamik sind beide überzeugend."
        )
    elif oma >= 75 and kurz < 60:
        status = "🏛️ Substanz stark + Zukunftsdynamik offen"
        summary = (
            "Die finanzielle Basis wirkt solide, während Wachstum "
            "und Dynamik noch keine ausreichende Stärke zeigen."
        )
    elif oma < 60 and kurz >= 75:
        status = "🚀 Zukunft stark + Substanz kritisch"
        summary = (
            "Die Wachstumsdynamik wirkt interessant, aber die "
            "finanzielle Substanz verdient besondere Aufmerksamkeit."
        )
    elif oma >= 60 and kurz >= 60:
        status = "⚖️ Substanz und Zukunft ausgewogen"
        summary = (
            "Beide Bereiche zeigen brauchbare Signale, ohne dass "
            "einer davon außergewöhnlich stark ist."
        )
    elif oma < 40 and kurz < 40:
        status = "🔴 Substanz und Zukunft schwach"
        summary = (
            "Sowohl die finanzielle Basis als auch die beobachtbare "
            "Wachstumsdynamik zeigen deutliche Schwächen."
        )
    else:
        status = "🟡 Gemischtes Bild"
        summary = (
            "Oma und Kurz liefern unterschiedliche Signale. "
            "Die offenen Punkte sollten genauer geprüft werden."
        )

    return {
        "status": status,
        "oma_score": oma,
        "kurz_score": kurz,
        "summary": summary,
        "note": (
            "Dieses Gesamtbild beschreibt Unternehmensqualität "
            "und Dynamik. Es ist keine Anlageempfehlung und "
            "keine Aussage darüber, ob eine Aktie günstig bewertet ist."
        ),
    }
  def build_story_reality_check(
    oma_score: Optional[dict],
    kurz_score: Optional[dict],
    evidence: Optional[dict],
) -> dict:
    """
    Stellt Zukunftsversprechen und finanzielle Substanz
    der verfügbaren Evidenz gegenüber.
    """

    oma = safe_float(
        oma_score.get("score")
        if oma_score
        else None
    )

    kurz = safe_float(
        kurz_score.get("score")
        if kurz_score
        else None
    )

    evidence_score = safe_float(
        evidence.get("score")
        if evidence
        else None
    )

    if oma is None or kurz is None or evidence_score is None:
        return {
            "status": "⚪ Nicht ausreichend bewertbar",
            "gap": None,
            "summary": (
                "Für einen Story-vs.-Reality-Check fehlen "
                "wichtige Daten."
            ),
        }

    story_gap = kurz - oma

    if evidence_score < 50:
        status = "🟠 Große Datenlücke"
        summary = (
            "Die vorhandene Datenbasis ist zu dünn, um "
            "Zukunftsversprechen zuverlässig mit der Realität "
            "abzugleichen."
        )
    elif story_gap >= 25:
        status = "🟡 Zukunftsgeschichte deutlich stärker als Substanz"
        summary = (
            "Die beobachtbare Zukunftsdynamik ist deutlich stärker "
            "als die aktuell sichtbare finanzielle Substanz."
        )
    elif story_gap <= -25:
        status = "🏛️ Substanz deutlich stärker als Zukunftsdynamik"
        summary = (
            "Die finanzielle Basis wirkt deutlich stärker als "
            "das derzeit beobachtbare Wachstum."
        )
    else:
        status = "🟢 Story und Realität relativ ausgewogen"
        summary = (
            "Wachstumsstory und finanzielle Substanz liegen "
            "vergleichsweise nah beieinander."
        )

    return {
        "status": status,
        "gap": story_gap,
        "oma_score": oma,
        "kurz_score": kurz,
        "evidence_score": evidence_score,
        "summary": summary,
        "note": (
            "Der Check bewertet keine Aussagen des Unternehmens "
            "als wahr oder falsch. Er zeigt lediglich, wie stark "
            "Wachstumsdynamik, Substanz und verfügbare Evidenz "
            "zueinander passen."
        ),
    }
  def build_analysis_summary(
    revenue_series: Optional[pd.Series],
    net_income_series: Optional[pd.Series],
    operating_cash_flow_series: Optional[pd.Series],
    fcf_series: Optional[pd.Series],
    cash_series: Optional[pd.Series],
    debt_series: Optional[pd.Series],
    share_series: Optional[pd.Series],
) -> dict:
    """
    Führt die wichtigsten OmaKurz-Analysebausteine zusammen.
    """

    revenue = clean_series(revenue_series)
    net_income = clean_series(net_income_series)
    ocf = clean_series(operating_cash_flow_series)
    fcf = clean_series(fcf_series)
    cash = clean_series(cash_series)
    debt = clean_series(debt_series)
    shares = clean_series(share_series)

    margin_series = calculate_margin_series(
        revenue,
        net_income,
    )

    acceleration = None

    if len(revenue) >= 3:
        growth_series = (
            revenue.pct_change()
            .replace([np.inf, -np.inf], np.nan)
            .dropna()
            * 100.0
        )

        acceleration = classify_acceleration(
            growth_series
        )

    margin_analysis = classify_margin_trend(
        margin_series
    )

    fcf_analysis = classify_fcf_dynamics(
        fcf
    )

    dilution_analysis = analyze_dilution(
        shares
    )

    latest_cash = (
        safe_float(cash.iloc[-1])
        if not cash.empty
        else None
    )

    latest_debt = (
        safe_float(debt.iloc[-1])
        if not debt.empty
        else None
    )

    net_cash = None

    if latest_cash is not None and latest_debt is not None:
        net_cash = latest_cash - latest_debt

    financing_cash_flow = None

    evidence = calculate_evidence(
        revenue,
        net_income,
        ocf,
        fcf,
        cash,
        debt,
        shares,
    )

    oma = build_oma_score(
        cash=latest_cash,
        debt=latest_debt,
        net_cash=net_cash,
        operating_cash_flow_series=ocf,
        fcf_series=fcf,
        margin_series=margin_series,
        dilution_analysis=dilution_analysis,
        evidence_score=evidence.get("score"),
    )

    kurz = build_kurz_score(
        revenue_series=revenue,
        acceleration_analysis=acceleration,
        margin_analysis=margin_analysis,
        evidence_score=evidence.get("score"),
    )

    core = build_core_judgment(
        oma_score=oma,
        kurz_score=kurz,
    )

    story_reality = build_story_reality_check(
        oma_score=oma,
        kurz_score=kurz,
        evidence=evidence,
    )

    financing = analyze_financing(
        cash=latest_cash,
        debt=latest_debt,
        net_cash=net_cash,
        financing_cash_flow=financing_cash_flow,
        fcf_series=fcf,
    )

    return {
        "margin_series": margin_series,
        "acceleration": acceleration,
        "margin_analysis": margin_analysis,
        "fcf_analysis": fcf_analysis,
        "dilution_analysis": dilution_analysis,
        "financing": financing,
        "evidence": evidence,
        "oma": oma,
        "kurz": kurz,
        "core": core,
        "story_reality": story_reality,
  }
  def get_analysis_label(
    analysis: Optional[dict],
    key: str = "status",
) -> str:
    """
    Holt sicher ein Anzeige-Label aus einem Analyse-Ergebnis.
    """

    if not analysis:
        return "⚪ Keine Daten"

    value = analysis.get(key)

    if value is None:
        return "⚪ Keine Daten"

    return str(value)
  
