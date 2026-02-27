"""
AdmitGuard — Strict Rule Validators
Sprint 1: Validates fields that have NO exception override.

Each validator function reads its rules from rules_config flags
and returns a dict: {"valid": bool, "error": str|None}
"""

import re
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rules_config as config


def validate_full_name(name):
    """Validate full name: required, min length, no numbers."""
    if not name or not name.strip():
        if config.RULE_NAME_REQUIRED:
            return {"valid": False, "error": "Full Name is required."}

    name = name.strip()

    if config.RULE_NAME_MIN_LENGTH and len(name) < config.RULE_NAME_MIN_LENGTH:
        return {
            "valid": False,
            "error": f"Full Name must be at least {config.RULE_NAME_MIN_LENGTH} characters."
        }

    if config.RULE_NAME_NO_NUMBERS and re.search(r'\d', name):
        return {"valid": False, "error": "Full Name must not contain numbers."}

    return {"valid": True, "error": None}


def validate_email(email, existing_emails=None):
    """Validate email: required, valid format, unique."""
    if not email or not email.strip():
        if config.RULE_EMAIL_REQUIRED:
            return {"valid": False, "error": "Email is required."}

    email = email.strip().lower()

    # Basic email format validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return {"valid": False, "error": "Please enter a valid email address."}

    # Uniqueness check
    if config.RULE_EMAIL_UNIQUE and existing_emails:
        if email in [e.lower() for e in existing_emails]:
            return {"valid": False, "error": "This email is already registered."}

    return {"valid": True, "error": None}


def validate_phone(phone):
    """Validate phone: 10-digit Indian number starting with 6/7/8/9."""
    if not phone or not phone.strip():
        if config.RULE_PHONE_REQUIRED:
            return {"valid": False, "error": "Phone number is required."}

    phone = phone.strip()

    # Remove any spaces or dashes
    phone_clean = re.sub(r'[\s\-]', '', phone)

    if not phone_clean.isdigit():
        return {"valid": False, "error": "Phone number must contain only digits."}

    if config.RULE_PHONE_LENGTH and len(phone_clean) != config.RULE_PHONE_LENGTH:
        return {
            "valid": False,
            "error": f"Phone number must be exactly {config.RULE_PHONE_LENGTH} digits."
        }

    if config.RULE_PHONE_VALID_START_DIGITS:
        first_digit = int(phone_clean[0])
        if first_digit not in config.RULE_PHONE_VALID_START_DIGITS:
            valid_starts = ', '.join(str(d) for d in config.RULE_PHONE_VALID_START_DIGITS)
            return {
                "valid": False,
                "error": f"Phone number must start with {valid_starts}."
            }

    return {"valid": True, "error": None}


def validate_qualification(qualification):
    """Validate highest qualification: must be from allowed list."""
    if not qualification or not qualification.strip():
        if config.RULE_QUALIFICATION_REQUIRED:
            return {"valid": False, "error": "Highest Qualification is required."}

    qualification = qualification.strip()

    if config.RULE_QUALIFICATION_ALLOWED_VALUES:
        if qualification not in config.RULE_QUALIFICATION_ALLOWED_VALUES:
            allowed = ', '.join(config.RULE_QUALIFICATION_ALLOWED_VALUES)
            return {
                "valid": False,
                "error": f"Qualification must be one of: {allowed}."
            }

    return {"valid": True, "error": None}


def validate_interview_status(status):
    """Validate interview status: must be valid value, blocked if Rejected."""
    if not status or not status.strip():
        if config.RULE_INTERVIEW_STATUS_REQUIRED:
            return {"valid": False, "error": "Interview Status is required."}

    status = status.strip()

    if config.RULE_INTERVIEW_VALID_VALUES:
        if status not in config.RULE_INTERVIEW_VALID_VALUES:
            valid = ', '.join(config.RULE_INTERVIEW_VALID_VALUES)
            return {
                "valid": False,
                "error": f"Interview Status must be one of: {valid}."
            }

    if config.RULE_INTERVIEW_BLOCK_ON_REJECTED and status == "Rejected":
        return {
            "valid": False,
            "error": "Candidate with 'Rejected' interview status cannot be submitted."
        }

    return {"valid": True, "error": None}


def validate_aadhaar(aadhaar):
    """Validate Aadhaar: exactly 12 digits, no alphabets."""
    if not aadhaar or not aadhaar.strip():
        if config.RULE_AADHAAR_REQUIRED:
            return {"valid": False, "error": "Aadhaar Number is required."}

    aadhaar = aadhaar.strip()

    if config.RULE_AADHAAR_DIGITS_ONLY and not aadhaar.isdigit():
        return {"valid": False, "error": "Aadhaar Number must contain only digits."}

    if config.RULE_AADHAAR_LENGTH and len(aadhaar) != config.RULE_AADHAAR_LENGTH:
        return {
            "valid": False,
            "error": f"Aadhaar Number must be exactly {config.RULE_AADHAAR_LENGTH} digits."
        }

    return {"valid": True, "error": None}


def validate_offer_letter(offer_letter, interview_status):
    """Validate offer letter: Yes/No, and Yes requires Cleared/Waitlisted interview."""
    if not offer_letter or not offer_letter.strip():
        if config.RULE_OFFER_LETTER_REQUIRED:
            return {"valid": False, "error": "Offer Letter Sent status is required."}

    offer_letter = offer_letter.strip()

    if config.RULE_OFFER_LETTER_VALID_VALUES:
        if offer_letter not in config.RULE_OFFER_LETTER_VALID_VALUES:
            valid = ', '.join(config.RULE_OFFER_LETTER_VALID_VALUES)
            return {
                "valid": False,
                "error": f"Offer Letter Sent must be one of: {valid}."
            }

    if config.RULE_OFFER_LETTER_REQUIRES_CLEARED_OR_WAITLISTED:
        if offer_letter == "Yes" and interview_status not in ["Cleared", "Waitlisted"]:
            return {
                "valid": False,
                "error": "Offer Letter can only be 'Yes' if Interview Status is 'Cleared' or 'Waitlisted'."
            }

    return {"valid": True, "error": None}


def validate_all_strict(data, existing_emails=None):
    """
    Run all strict validations on candidate data.
    Returns dict of field -> validation result.
    """
    results = {}

    results["full_name"] = validate_full_name(data.get("full_name", ""))
    results["email"] = validate_email(data.get("email", ""), existing_emails)
    results["phone"] = validate_phone(data.get("phone", ""))
    results["highest_qualification"] = validate_qualification(
        data.get("highest_qualification", "")
    )
    results["interview_status"] = validate_interview_status(
        data.get("interview_status", "")
    )
    results["aadhaar"] = validate_aadhaar(data.get("aadhaar", ""))
    results["offer_letter_sent"] = validate_offer_letter(
        data.get("offer_letter_sent", ""),
        data.get("interview_status", "")
    )

    return results
