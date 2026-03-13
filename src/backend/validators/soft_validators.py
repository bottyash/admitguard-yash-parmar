"""
AdmitGuard v2 — Tier 2: SOFT FLAG Validators
If Tier 2 rules fail, data IS saved but the candidate is flagged for review.
These are concerns, not blockers.

Checks: education gaps, backlogs, career gaps, domain transitions,
        no work after education, scores below threshold.
"""

import rules_config


def validate_all_soft(candidate_data, education_result=None, work_result=None,
                      cohort_rules=None):
    """
    Run all Tier 2 (soft flag) checks.

    Args:
        candidate_data: dict of candidate fields
        education_result: output from validate_all_education()
        work_result: output from validate_all_work()
        cohort_rules: dict from get_effective_rules()

    Returns: list of flag dicts: [{"type": str, "field": str, "message": str, "severity": str}]
    """
    rules = cohort_rules or {}
    flags = []

    # --- Education gap ---
    if education_result:
        max_gap = rules.get(
            "max_education_gap_months",
            rules_config.RULE_MAX_EDUCATION_GAP_MONTHS
        )
        total_gap = education_result.get("total_gap_months", 0)
        if total_gap > max_gap:
            flags.append({
                "type": "EDUCATION_GAP",
                "field": "education",
                "message": f"Total education gap ({total_gap} months) exceeds threshold ({max_gap} months).",
                "severity": "warning",
            })

        # --- Backlogs ---
        total_backlogs = education_result.get("total_backlogs", 0)
        if rules_config.RULE_FLAG_ON_BACKLOGS and total_backlogs > 0:
            flags.append({
                "type": "BACKLOGS",
                "field": "education",
                "message": f"Candidate has {total_backlogs} backlog(s).",
                "severity": "warning" if total_backlogs <= 3 else "high",
            })

        # --- Score below threshold ---
        score_threshold = rules.get(
            "score_threshold_percentage",
            rules_config.RULE_SCORE_THRESHOLD_PERCENTAGE
        )
        for entry in education_result.get("entries", []):
            normalized = entry.get("normalized_score", 0)
            level = entry.get("level", "")
            if normalized > 0 and normalized < score_threshold:
                flags.append({
                    "type": "LOW_SCORE",
                    "field": f"education.{level}",
                    "message": f"{level} score ({normalized}%) is below threshold ({score_threshold}%).",
                    "severity": "warning",
                })

    # --- Career gaps ---
    if work_result:
        derived = work_result.get("derived", {})
        max_career_gap = rules.get(
            "max_career_gap_months",
            rules_config.RULE_MAX_CAREER_GAP_MONTHS
        )

        for gap in derived.get("career_gaps", []):
            if gap["gap_months"] > max_career_gap:
                flags.append({
                    "type": "CAREER_GAP",
                    "field": "work",
                    "message": (
                        f"Career gap of {gap['gap_months']} months "
                        f"({gap['from_date']} to {gap['to_date']}) "
                        f"exceeds threshold ({max_career_gap} months)."
                    ),
                    "severity": "warning",
                })

        # --- Domain transitions ---
        max_transitions = rules.get(
            "max_domain_transitions",
            rules_config.RULE_MAX_DOMAIN_TRANSITIONS
        )
        transitions = derived.get("domain_transitions", 0)
        if transitions > max_transitions:
            flags.append({
                "type": "DOMAIN_TRANSITIONS",
                "field": "work",
                "message": f"{transitions} domain transitions (threshold: {max_transitions}). May indicate career instability.",
                "severity": "warning",
            })

    # --- No work after education ---
    if education_result and (not work_result or not work_result.get("entries")):
        from datetime import datetime
        max_years = rules.get(
            "years_since_education_no_work",
            rules_config.RULE_YEARS_SINCE_EDUCATION_NO_WORK
        )

        # Find most recent education year
        latest_year = 0
        for entry in education_result.get("entries", []):
            yr = entry.get("year_of_passing")
            if yr and int(yr) > latest_year:
                latest_year = int(yr)

        if latest_year > 0:
            years_since = datetime.now().year - latest_year
            if years_since > max_years:
                flags.append({
                    "type": "NO_WORK_AFTER_EDUCATION",
                    "field": "work",
                    "message": (
                        f"{years_since} years since last education with no work experience. "
                        f"Threshold: {max_years} years."
                    ),
                    "severity": "high",
                })

    return flags


def is_flagged_for_review(flags):
    """Return True if flags warrant manual review."""
    if not flags:
        return False
    # Any flag = review needed
    return len(flags) > 0


def count_flags_by_severity(flags):
    """Count flags by severity level."""
    counts = {"warning": 0, "high": 0}
    for f in flags:
        severity = f.get("severity", "warning")
        counts[severity] = counts.get(severity, 0) + 1
    return counts


# =============================================================================
# Legacy compatibility functions (used by old routes, will be removed later)
# =============================================================================

def count_exceptions(soft_results):
    """Legacy: count exceptions from old-style soft_results dict."""
    if isinstance(soft_results, list):
        return len(soft_results)
    count = 0
    for field, result in soft_results.items():
        if isinstance(result, dict) and result.get("exception_applied"):
            count += 1
    return count


def validate_date_of_birth(dob):
    """Legacy stub — handled by strict_validators.validate_age."""
    return {"valid": True, "error": None, "exception_allowed": False}


def validate_graduation_year(year):
    """Legacy stub — handled by education_validators."""
    return {"valid": True, "error": None, "exception_allowed": False}


def validate_percentage_cgpa(score, score_type="percentage"):
    """Legacy stub — handled by education_validators."""
    return {"valid": True, "error": None, "exception_allowed": False}


def validate_screening_score(score):
    """Legacy stub — handled by Tier 2 in v2."""
    return {"valid": True, "error": None, "exception_allowed": False}


def validate_rationale(rationale):
    """Legacy: validate exception rationale."""
    rationale = (rationale or "").strip()
    if not rationale:
        return {"valid": False, "error": "Rationale is required for exceptions."}
    if len(rationale) < rules_config.RULE_RATIONALE_MIN_LENGTH:
        return {
            "valid": False,
            "error": f"Rationale must be at least {rules_config.RULE_RATIONALE_MIN_LENGTH} characters.",
        }
    return {"valid": True, "error": None}
