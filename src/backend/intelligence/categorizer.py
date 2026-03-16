"""
AdmitGuard v2 — Auto-Categorizer
Assigns candidates to categories based on risk score thresholds.
"""

import rules_config


def categorize(risk_score, cohort_rules=None):
    """
    Categorize a candidate based on their risk score.

    Categories:
      - Strong Fit:   risk_score <= CATEGORY_STRONG_FIT_MAX (default 30)
      - Needs Review:  risk_score <= CATEGORY_NEEDS_REVIEW_MAX (default 60)
      - Weak Fit:     risk_score > CATEGORY_NEEDS_REVIEW_MAX

    Returns: {"category": str, "confidence": str}
    """
    rules = cohort_rules or {}

    strong_max = rules.get(
        "category_strong_fit_max",
        rules_config.CATEGORY_STRONG_FIT_MAX
    )
    review_max = rules.get(
        "category_needs_review_max",
        rules_config.CATEGORY_NEEDS_REVIEW_MAX
    )

    if risk_score <= strong_max:
        return {
            "category": "Strong Fit",
            "confidence": "high" if risk_score <= strong_max * 0.5 else "moderate",
        }
    elif risk_score <= review_max:
        return {
            "category": "Needs Review",
            "confidence": "moderate",
        }
    else:
        return {
            "category": "Weak Fit",
            "confidence": "high" if risk_score >= 80 else "moderate",
        }
