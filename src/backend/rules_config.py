"""
AdmitGuard — Rules Configuration (Flags-Based)
Sprint 2: Strict Rules + Soft Rules with Exception System

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

# =============================================================================
# SOFT RULES — Exception allowed with valid rationale
# =============================================================================

# --- Date of Birth / Age ---
RULE_AGE_CHECK_ENABLED = True
RULE_AGE_MIN = 18
RULE_AGE_MAX = 35
RULE_AGE_EXCEPTION_ALLOWED = True

# --- Graduation Year ---
RULE_GRAD_YEAR_CHECK_ENABLED = True
RULE_GRAD_YEAR_MIN = 2015
RULE_GRAD_YEAR_MAX = 2025
RULE_GRAD_YEAR_EXCEPTION_ALLOWED = True

# --- Percentage / CGPA ---
RULE_SCORE_CHECK_ENABLED = True
RULE_PERCENTAGE_MIN = 60.0
RULE_CGPA_MIN = 6.0
RULE_CGPA_SCALE = 10.0
RULE_SCORE_EXCEPTION_ALLOWED = True

# --- Screening Test Score ---
RULE_SCREENING_CHECK_ENABLED = True
RULE_SCREENING_SCORE_MIN = 40
RULE_SCREENING_SCORE_MAX = 100
RULE_SCREENING_EXCEPTION_ALLOWED = True

# =============================================================================
# RATIONALE VALIDATION — Required when overriding soft rules
# =============================================================================

RULE_RATIONALE_MIN_LENGTH = 30
RULE_RATIONALE_REQUIRED_KEYWORDS = [
    "approved by",
    "special case",
    "documentation pending",
    "waiver granted"
]

# =============================================================================
# EXCEPTION FLAGGING — System rule (computed, not editable by operator)
# =============================================================================

RULE_MAX_EXCEPTIONS_BEFORE_FLAG = 2
# If a candidate has more than this many exceptions, flag for manager review
