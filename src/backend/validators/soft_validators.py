"""
AdmitGuard — Soft Rule Validators
Sprint 2: Validates fields that CAN be overridden with a rationale.

Each validator returns:
{
    "valid": bool,           # Whether the value passes the rule
    "error": str|None,       # Error message if invalid
    "rule_type": "soft",     # Always "soft" for these validators
    "exception_allowed": bool # Whether this rule can be overridden
}

If the field fails validation but exception is enabled with valid rationale,
the submission is still allowed.
"""

import re
import sys
import os
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rules_config as config


def validate_date_of_birth(dob_str):
    """
    Validate Date of Birth: age must be between 18 and 35 at program start.
    Soft rule — exception with rationale allowed.
    """
    if not dob_str or not dob_str.strip():
        return {
            "valid": False,
            "error": "Date of Birth is required.",
            "rule_type": "soft",
            "exception_allowed": config.RULE_AGE_EXCEPTION_ALLOWED,
        }

    dob_str = dob_str.strip()

    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
    except ValueError:
        return {
            "valid": False,
            "error": "Date of Birth must be in YYYY-MM-DD format.",
            "rule_type": "soft",
            "exception_allowed": False,  # format error is strict
        }

    if not config.RULE_AGE_CHECK_ENABLED:
        return {"valid": True, "error": None, "rule_type": "soft", "exception_allowed": False}

    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    if age < config.RULE_AGE_MIN:
        return {
            "valid": False,
            "error": f"Candidate must be at least {config.RULE_AGE_MIN} years old. Current age: {age}.",
            "rule_type": "soft",
            "exception_allowed": config.RULE_AGE_EXCEPTION_ALLOWED,
        }

    if age > config.RULE_AGE_MAX:
        return {
            "valid": False,
            "error": f"Candidate must be at most {config.RULE_AGE_MAX} years old. Current age: {age}.",
            "rule_type": "soft",
            "exception_allowed": config.RULE_AGE_EXCEPTION_ALLOWED,
        }

    return {"valid": True, "error": None, "rule_type": "soft", "exception_allowed": False}


def validate_graduation_year(year_str):
    """
    Validate Graduation Year: must be between 2015 and 2025.
    Soft rule — exception with rationale allowed.
    """
    if not year_str and year_str != 0:
        return {
            "valid": False,
            "error": "Graduation Year is required.",
            "rule_type": "soft",
            "exception_allowed": config.RULE_GRAD_YEAR_EXCEPTION_ALLOWED,
        }

    try:
        year = int(year_str)
    except (ValueError, TypeError):
        return {
            "valid": False,
            "error": "Graduation Year must be a valid number.",
            "rule_type": "soft",
            "exception_allowed": False,
        }

    if not config.RULE_GRAD_YEAR_CHECK_ENABLED:
        return {"valid": True, "error": None, "rule_type": "soft", "exception_allowed": False}

    if year < config.RULE_GRAD_YEAR_MIN or year > config.RULE_GRAD_YEAR_MAX:
        return {
            "valid": False,
            "error": f"Graduation Year must be between {config.RULE_GRAD_YEAR_MIN} and {config.RULE_GRAD_YEAR_MAX}. Got: {year}.",
            "rule_type": "soft",
            "exception_allowed": config.RULE_GRAD_YEAR_EXCEPTION_ALLOWED,
        }

    return {"valid": True, "error": None, "rule_type": "soft", "exception_allowed": False}


def validate_percentage_cgpa(value_str, score_type="percentage"):
    """
    Validate Percentage/CGPA:
    - If percentage: ≥60%
    - If CGPA (10-point scale): ≥6.0
    Soft rule — exception with rationale allowed.
    """
    if not value_str and value_str != 0:
        return {
            "valid": False,
            "error": "Percentage/CGPA is required.",
            "rule_type": "soft",
            "exception_allowed": config.RULE_SCORE_EXCEPTION_ALLOWED,
        }

    try:
        value = float(value_str)
    except (ValueError, TypeError):
        return {
            "valid": False,
            "error": "Percentage/CGPA must be a valid number.",
            "rule_type": "soft",
            "exception_allowed": False,
        }

    if not config.RULE_SCORE_CHECK_ENABLED:
        return {"valid": True, "error": None, "rule_type": "soft", "exception_allowed": False}

    score_type = (score_type or "percentage").strip().lower()

    if score_type == "cgpa":
        if value < 0 or value > config.RULE_CGPA_SCALE:
            return {
                "valid": False,
                "error": f"CGPA must be between 0 and {config.RULE_CGPA_SCALE}.",
                "rule_type": "soft",
                "exception_allowed": False,
            }
        if value < config.RULE_CGPA_MIN:
            return {
                "valid": False,
                "error": f"CGPA must be at least {config.RULE_CGPA_MIN}. Got: {value}.",
                "rule_type": "soft",
                "exception_allowed": config.RULE_SCORE_EXCEPTION_ALLOWED,
            }
    else:  # percentage
        if value < 0 or value > 100:
            return {
                "valid": False,
                "error": "Percentage must be between 0 and 100.",
                "rule_type": "soft",
                "exception_allowed": False,
            }
        if value < config.RULE_PERCENTAGE_MIN:
            return {
                "valid": False,
                "error": f"Percentage must be at least {config.RULE_PERCENTAGE_MIN}%. Got: {value}%.",
                "rule_type": "soft",
                "exception_allowed": config.RULE_SCORE_EXCEPTION_ALLOWED,
            }

    return {"valid": True, "error": None, "rule_type": "soft", "exception_allowed": False}


def validate_screening_score(score_str):
    """
    Validate Screening Test Score: ≥40 out of 100.
    Soft rule — exception with rationale allowed.
    """
    if not score_str and score_str != 0:
        return {
            "valid": False,
            "error": "Screening Test Score is required.",
            "rule_type": "soft",
            "exception_allowed": config.RULE_SCREENING_EXCEPTION_ALLOWED,
        }

    try:
        score = float(score_str)
    except (ValueError, TypeError):
        return {
            "valid": False,
            "error": "Screening Test Score must be a valid number.",
            "rule_type": "soft",
            "exception_allowed": False,
        }

    if not config.RULE_SCREENING_CHECK_ENABLED:
        return {"valid": True, "error": None, "rule_type": "soft", "exception_allowed": False}

    if score < 0 or score > config.RULE_SCREENING_SCORE_MAX:
        return {
            "valid": False,
            "error": f"Screening Test Score must be between 0 and {config.RULE_SCREENING_SCORE_MAX}.",
            "rule_type": "soft",
            "exception_allowed": False,
        }

    if score < config.RULE_SCREENING_SCORE_MIN:
        return {
            "valid": False,
            "error": f"Screening Test Score must be at least {config.RULE_SCREENING_SCORE_MIN}. Got: {score}.",
            "rule_type": "soft",
            "exception_allowed": config.RULE_SCREENING_EXCEPTION_ALLOWED,
        }

    return {"valid": True, "error": None, "rule_type": "soft", "exception_allowed": False}


def validate_rationale(rationale):
    """
    Validate exception rationale:
    - Minimum 30 characters
    - Must contain at least one required keyword
    """
    if not rationale or not rationale.strip():
        return {
            "valid": False,
            "error": "Rationale is required when requesting an exception.",
        }

    rationale = rationale.strip()

    if len(rationale) < config.RULE_RATIONALE_MIN_LENGTH:
        return {
            "valid": False,
            "error": f"Rationale must be at least {config.RULE_RATIONALE_MIN_LENGTH} characters. Currently: {len(rationale)}.",
        }

    # Check for at least one required keyword (case-insensitive)
    rationale_lower = rationale.lower()
    has_keyword = any(
        keyword.lower() in rationale_lower
        for keyword in config.RULE_RATIONALE_REQUIRED_KEYWORDS
    )

    if not has_keyword:
        keywords = '", "'.join(config.RULE_RATIONALE_REQUIRED_KEYWORDS)
        return {
            "valid": False,
            "error": f'Rationale must include at least one keyword: "{keywords}".',
        }

    return {"valid": True, "error": None}


def validate_all_soft(data, exceptions=None):
    """
    Run all soft validations on candidate data.
    
    Args:
        data: candidate fields dict
        exceptions: dict of field_name -> {"enabled": bool, "rationale": str}
    
    Returns dict of field -> {
        "valid": bool,
        "error": str|None,
        "rule_type": "soft",
        "exception_allowed": bool,
        "exception_applied": bool,
        "rationale_valid": bool|None,
        "rationale_error": str|None,
    }
    """
    exceptions = exceptions or {}
    results = {}

    # Define soft field validators
    soft_checks = {
        "date_of_birth": lambda: validate_date_of_birth(data.get("date_of_birth", "")),
        "graduation_year": lambda: validate_graduation_year(data.get("graduation_year", "")),
        "percentage_cgpa": lambda: validate_percentage_cgpa(
            data.get("percentage_cgpa", ""),
            data.get("score_type", "percentage"),
        ),
        "screening_test_score": lambda: validate_screening_score(
            data.get("screening_test_score", "")
        ),
    }

    for field_name, validator in soft_checks.items():
        result = validator()

        # If field fails and exception is enabled, validate the rationale
        exception_info = exceptions.get(field_name, {})
        exception_enabled = exception_info.get("enabled", False)

        result["exception_applied"] = False
        result["rationale_valid"] = None
        result["rationale_error"] = None

        if not result["valid"] and result.get("exception_allowed") and exception_enabled:
            rationale = exception_info.get("rationale", "")
            rationale_result = validate_rationale(rationale)

            result["rationale_valid"] = rationale_result["valid"]
            result["rationale_error"] = rationale_result.get("error")

            if rationale_result["valid"]:
                # Exception accepted — mark as valid with exception
                result["exception_applied"] = True
                result["valid"] = True
                result["error"] = None

        results[field_name] = result

    return results


def count_exceptions(soft_results):
    """Count how many exceptions were applied."""
    return sum(1 for r in soft_results.values() if r.get("exception_applied"))


def is_flagged_for_review(exception_count):
    """Check if the candidate should be flagged for manager review."""
    return exception_count > config.RULE_MAX_EXCEPTIONS_BEFORE_FLAG
