"""
AdmitGuard — Rules Configuration (Flags-Based)
Sprint 1: Strict Rules Only

All eligibility rules are defined as flags/constants here.
To modify rules, change the values below — no code changes needed elsewhere.
"""

# =============================================================================
# STRICT RULES — No exceptions allowed, form blocks on violation
# =============================================================================

# --- Full Name ---
RULE_NAME_REQUIRED = True
RULE_NAME_MIN_LENGTH = 2
RULE_NAME_NO_NUMBERS = True

# --- Email ---
RULE_EMAIL_REQUIRED = True
RULE_EMAIL_UNIQUE = True

# --- Phone ---
RULE_PHONE_REQUIRED = True
RULE_PHONE_LENGTH = 10
RULE_PHONE_VALID_START_DIGITS = [6, 7, 8, 9]

# --- Highest Qualification ---
RULE_QUALIFICATION_REQUIRED = True
RULE_QUALIFICATION_ALLOWED_VALUES = [
    "B.Tech", "B.E.", "B.Sc", "BCA",
    "M.Tech", "M.Sc", "MCA", "MBA"
]

# --- Interview Status ---
RULE_INTERVIEW_STATUS_REQUIRED = True
RULE_INTERVIEW_VALID_VALUES = ["Cleared", "Waitlisted", "Rejected"]
RULE_INTERVIEW_BLOCK_ON_REJECTED = True

# --- Aadhaar Number ---
RULE_AADHAAR_REQUIRED = True
RULE_AADHAAR_LENGTH = 12
RULE_AADHAAR_DIGITS_ONLY = True

# --- Offer Letter Sent ---
RULE_OFFER_LETTER_REQUIRED = True
RULE_OFFER_LETTER_VALID_VALUES = ["Yes", "No"]
RULE_OFFER_LETTER_REQUIRES_CLEARED_OR_WAITLISTED = True
# Offer Letter can only be "Yes" if Interview Status is "Cleared" or "Waitlisted"
