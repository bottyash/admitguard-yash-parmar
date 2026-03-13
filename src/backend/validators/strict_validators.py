"""
AdmitGuard v2 — Tier 1: HARD REJECT Validators
If any Tier 1 rule fails, the submission is rejected outright.
Data is NOT saved to the database.

Checks: mandatory fields, format validation, duplicates, age, score ranges.
"""

import re
from datetime import datetime, date
import rules_config


def validate_all_strict(data, existing_emails=None, existing_phones=None,
                        cohort_rules=None):
    """
    Run all Tier 1 (hard reject) validations on candidate data.
    cohort_rules: dict from get_effective_rules() — uses defaults if None.

    Returns: dict of {field: {"valid": bool, "error": str|None}}
    """
    existing_emails = existing_emails or []
    existing_phones = existing_phones or []
    rules = cohort_rules or {}

    results = {}

    results["full_name"] = validate_full_name(data.get("full_name", ""))
    results["email"] = validate_email(data.get("email", ""), existing_emails)
    results["phone"] = validate_phone(
        data.get("phone", ""), existing_phones
    )
    results["date_of_birth"] = validate_age(
        data.get("date_of_birth", ""),
        min_age=rules.get("age_minimum", rules_config.RULE_AGE_MINIMUM)
    )
    results["aadhaar"] = validate_aadhaar(data.get("aadhaar", ""))

    # Check mandatory fields
    for field in rules_config.MANDATORY_FIELDS:
        if field not in results:
            value = data.get(field, "")
            if not value or not str(value).strip():
                results[field] = {
                    "valid": False,
                    "error": f"{field.replace('_', ' ').title()} is required.",
                }

    return results


# =============================================================================
# Individual validators
# =============================================================================

def validate_full_name(name):
    """Name must be ≥2 chars, no numbers."""
    name = (name or "").strip()
    if not name:
        return {"valid": False, "error": "Full name is required."}
    if len(name) < rules_config.RULE_NAME_MIN_LENGTH:
        return {"valid": False, "error": f"Name must be at least {rules_config.RULE_NAME_MIN_LENGTH} characters."}
    if rules_config.RULE_NAME_NO_NUMBERS and re.search(r'\d', name):
        return {"valid": False, "error": "Name must not contain numbers."}
    return {"valid": True, "error": None}


def validate_email(email, existing_emails=None):
    """Valid email format + unique."""
    email = (email or "").strip().lower()
    if not email:
        return {"valid": False, "error": "Email is required."}

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return {"valid": False, "error": "Invalid email format."}

    if rules_config.RULE_DUPLICATE_EMAIL and existing_emails:
        if email in [e.lower() for e in existing_emails]:
            return {"valid": False, "error": "This email is already registered."}

    return {"valid": True, "error": None}


def validate_phone(phone, existing_phones=None):
    """Indian phone: 10 digits, starts with 6-9."""
    phone = (phone or "").strip()
    phone_digits = re.sub(r'[^0-9]', '', phone)

    if not phone_digits:
        return {"valid": False, "error": "Phone number is required."}

    if len(phone_digits) != rules_config.RULE_PHONE_LENGTH:
        return {"valid": False, "error": f"Phone must be exactly {rules_config.RULE_PHONE_LENGTH} digits."}

    if int(phone_digits[0]) not in rules_config.RULE_PHONE_VALID_START_DIGITS:
        return {"valid": False, "error": "Indian phone must start with 6, 7, 8, or 9."}

    if rules_config.RULE_DUPLICATE_PHONE and existing_phones:
        if phone_digits in [re.sub(r'[^0-9]', '', p) for p in existing_phones]:
            return {"valid": False, "error": "This phone number is already registered."}

    return {"valid": True, "error": None}


def validate_age(dob_str, min_age=None):
    """Date of birth must make candidate at least min_age years old."""
    if min_age is None:
        min_age = rules_config.RULE_AGE_MINIMUM

    dob_str = (dob_str or "").strip()
    if not dob_str:
        return {"valid": False, "error": "Date of birth is required."}

    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
    except ValueError:
        return {"valid": False, "error": "Invalid date format. Use YYYY-MM-DD."}

    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    if age < min_age:
        return {"valid": False, "error": f"Candidate must be at least {min_age} years old."}

    if dob > today:
        return {"valid": False, "error": "Date of birth cannot be in the future."}

    return {"valid": True, "error": None}


def validate_aadhaar(aadhaar):
    """Aadhaar must be exactly 12 digits."""
    aadhaar = (aadhaar or "").strip()
    if not aadhaar:
        return {"valid": False, "error": "Aadhaar number is required."}

    aadhaar_digits = re.sub(r'[^0-9]', '', aadhaar)

    if len(aadhaar_digits) != rules_config.RULE_AADHAAR_LENGTH:
        return {"valid": False, "error": f"Aadhaar must be exactly {rules_config.RULE_AADHAAR_LENGTH} digits."}

    if rules_config.RULE_AADHAAR_DIGITS_ONLY and not aadhaar_digits.isdigit():
        return {"valid": False, "error": "Aadhaar must contain only digits."}

    return {"valid": True, "error": None}


# Legacy compatibility — old routes may call these
def validate_qualification(qual):
    """Kept for backward compatibility. Always passes in v2 (handled by education_validators)."""
    return {"valid": True, "error": None}

def validate_interview_status(status):
    """Kept for backward compatibility."""
    return {"valid": True, "error": None}

def validate_offer_letter(offer, interview_status=""):
    """Kept for backward compatibility."""
    return {"valid": True, "error": None}
