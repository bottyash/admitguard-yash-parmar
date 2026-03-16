"""
AdmitGuard v2 — Risk Scorer
Computes a 0-100 risk score based on weighted factors from the candidate's
education and work history. Lower = better candidate.
"""

import rules_config


def compute_risk_score(education_result=None, work_result=None,
                       completeness_pct=0, cohort_rules=None):
    """
    Compute a weighted 0-100 risk score.

    Components (from rules_config.RISK_WEIGHTS):
      - education_gaps: 15%
      - backlogs: 20%
      - score_trend: 15%
      - work_relevance: 15%
      - career_gaps: 10%
      - domain_switches: 10%
      - completeness: 15%

    Returns: {"risk_score": float, "breakdown": {factor: sub_score}}
    """
    weights = rules_config.RISK_WEIGHTS
    breakdown = {}

    # --- 1. Education Gaps (15%) ---
    edu_gap = 0
    if education_result:
        gap_months = education_result.get("total_gap_months", 0)
        # Normalize: 0 gap = 0 risk, RISK_MAX_EDUCATION_GAP = 100 risk
        edu_gap = min(100, (gap_months / rules_config.RISK_MAX_EDUCATION_GAP) * 100)
    breakdown["education_gaps"] = round(edu_gap, 1)

    # --- 2. Backlogs (20%) ---
    backlog_score = 0
    if education_result:
        backlogs = education_result.get("total_backlogs", 0)
        backlog_score = min(100, (backlogs / rules_config.RISK_MAX_BACKLOGS) * 100)
    breakdown["backlogs"] = round(backlog_score, 1)

    # --- 3. Score Trend (15%) ---
    trend_score = 50  # Neutral default
    if education_result:
        entries = education_result.get("entries", [])
        normalized_scores = [
            e.get("normalized_score", 0)
            for e in entries
            if e.get("normalized_score", 0) > 0
        ]
        if len(normalized_scores) >= 2:
            # Compare first vs last score
            first = normalized_scores[0]
            last = normalized_scores[-1]
            if last >= first:
                # Improving — lower risk (0 = great improvement)
                improvement = min(30, last - first)
                trend_score = max(0, 50 - improvement * 1.67)
            else:
                # Declining — higher risk
                decline = first - last
                trend_score = min(100, 50 + decline * 1.67)
    breakdown["score_trend"] = round(trend_score, 1)

    # --- 4. Work Relevance (15%) ---
    relevance_score = 50  # Default: no work = neutral-high
    if work_result:
        derived = work_result.get("derived", {})
        total = derived.get("total_experience_months", 0)
        relevant = derived.get("domain_relevant_months", 0)

        if total > 0:
            relevance_pct = (relevant / total) * 100
            # High relevance = low risk
            relevance_score = max(0, 100 - relevance_pct)
        elif total == 0:
            relevance_score = 60  # No experience = moderate risk
    breakdown["work_relevance"] = round(relevance_score, 1)

    # --- 5. Career Gaps (10%) ---
    career_gap_score = 0
    if work_result:
        derived = work_result.get("derived", {})
        gap_months = derived.get("total_gap_months", 0)
        career_gap_score = min(100, (gap_months / rules_config.RISK_MAX_CAREER_GAP) * 100)
    breakdown["career_gaps"] = round(career_gap_score, 1)

    # --- 6. Domain Switches (10%) ---
    switch_score = 0
    if work_result:
        derived = work_result.get("derived", {})
        switches = derived.get("domain_transitions", 0)
        switch_score = min(100, (switches / rules_config.RISK_MAX_DOMAIN_SWITCHES) * 100)
    breakdown["domain_switches"] = round(switch_score, 1)

    # --- 7. Completeness (15%) ---
    # High completeness = low risk
    completeness_risk = max(0, 100 - completeness_pct)
    breakdown["completeness"] = round(completeness_risk, 1)

    # --- Weighted total ---
    total_weight = sum(weights.values())
    risk_score = 0
    for factor, weight in weights.items():
        sub_score = breakdown.get(factor, 50)
        risk_score += (sub_score * weight) / total_weight

    risk_score = round(min(100, max(0, risk_score)), 1)

    return {
        "risk_score": risk_score,
        "breakdown": breakdown,
    }
