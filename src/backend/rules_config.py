"""
AdmitGuard v2 — Rules Configuration
3-tier validation rules + education pathways + risk scoring weights.

All values here are DEFAULTS. Per-cohort overrides are loaded from
the cohort_params table at runtime via models/cohort.py.
"""

# =============================================================================
# TIER 1: HARD REJECT — Data cannot be saved if violated
# =============================================================================

# --- Mandatory Fields ---
MANDATORY_FIELDS = ["full_name", "email", "phone", "date_of_birth", "aadhaar"]

# --- Full Name ---
RULE_NAME_MIN_LENGTH = 2
RULE_NAME_NO_NUMBERS = True

# --- Email ---
RULE_EMAIL_UNIQUE = True

# --- Phone ---
RULE_PHONE_LENGTH = 10
RULE_PHONE_VALID_START_DIGITS = [6, 7, 8, 9]

# --- Age ---
RULE_AGE_MINIMUM = 18

# --- Aadhaar ---
RULE_AADHAAR_LENGTH = 12
RULE_AADHAAR_DIGITS_ONLY = True

# --- Score Ranges ---
RULE_SCORE_MAX_PERCENTAGE = 100.0
RULE_SCORE_MAX_CGPA_10 = 10.0
RULE_SCORE_MAX_CGPA_4 = 4.0

# --- Duplicate Detection ---
RULE_DUPLICATE_EMAIL = True
RULE_DUPLICATE_PHONE = True

# =============================================================================
# TIER 2: SOFT FLAG — Data saved, but flagged for manual review
# =============================================================================

# --- Education Gaps ---
RULE_MAX_EDUCATION_GAP_MONTHS = 24  # Total gap across all levels

# --- Backlogs ---
RULE_FLAG_ON_BACKLOGS = True  # Any backlog > 0 triggers flag

# --- Career Gaps ---
RULE_MAX_CAREER_GAP_MONTHS = 6  # Gap between jobs

# --- Domain Transitions ---
RULE_MAX_DOMAIN_TRANSITIONS = 3  # Unrelated domain switches in work history

# --- No Work After Education ---
RULE_YEARS_SINCE_EDUCATION_NO_WORK = 3  # Years since last education with no work

# --- Score Thresholds (below = flag, not reject) ---
RULE_SCORE_THRESHOLD_PERCENTAGE = 60.0
RULE_SCORE_THRESHOLD_CGPA_10 = 6.0
RULE_SCORE_THRESHOLD_CGPA_4 = 2.5

# --- Screening Test ---
RULE_SCREENING_SCORE_MIN = 40
RULE_SCREENING_SCORE_MAX = 100

# =============================================================================
# TIER 3: ENRICHMENT — Auto-computed metadata attached to record
# =============================================================================

# --- Experience Buckets ---
EXPERIENCE_BUCKETS = {
    "Fresher": (0, 0),          # 0 months
    "Junior": (1, 24),          # 1-24 months (0-2 years)
    "Mid": (25, 60),            # 25-60 months (2-5 years)
    "Senior": (61, float("inf")),  # 61+ months (5+ years)
}

# --- Risk Score Categories ---
CATEGORY_STRONG_FIT_MAX = 30    # risk_score <= 30
CATEGORY_NEEDS_REVIEW_MAX = 60  # risk_score 31-60
# Above 60 = Weak Fit

# =============================================================================
# EDUCATION PATHWAYS — Indian Education System
# =============================================================================

VALID_EDUCATION_LEVELS = ["10th", "12th", "Diploma", "ITI", "UG", "PG", "PhD"]

# Which levels are required per path
EDUCATION_PATHS = {
    "A": {
        "name": "Standard (10th → 12th → UG)",
        "required": ["10th", "12th", "UG"],
        "optional": ["PG", "PhD"],
    },
    "B": {
        "name": "Diploma (10th → Diploma → UG Lateral Entry)",
        "required": ["10th", "Diploma", "UG"],
        "optional": ["12th", "PG", "PhD"],
    },
    "C": {
        "name": "Lateral (10th → ITI → Diploma → UG)",
        "required": ["10th", "ITI", "Diploma", "UG"],
        "optional": ["12th", "PG", "PhD"],
    },
}

# Level sort order (for chronological validation)
EDUCATION_LEVEL_ORDER = {
    "10th": 1,
    "12th": 2,
    "ITI": 2,       # Same tier as 12th
    "Diploma": 3,
    "UG": 4,
    "PG": 5,
    "PhD": 6,
}

# Score scales and normalization
SCORE_SCALES = {
    "percentage": {"max": 100, "to_percentage": lambda x: x},
    "cgpa_10": {"max": 10, "to_percentage": lambda x: x * 9.5},
    "cgpa_4": {"max": 4, "to_percentage": lambda x: x * 25},
    "grade": {"max": None, "to_percentage": None},  # Manual mapping needed
}

# Known Indian boards (for autocomplete + LLM verification)
KNOWN_BOARDS_10TH_12TH = [
    "CBSE", "ICSE", "ISC", "SSC", "HSC",
    "Maharashtra Board", "Karnataka Board", "Tamil Nadu Board",
    "UP Board", "Bihar Board", "MP Board", "Rajasthan Board",
    "Gujarat Board", "AP Board", "Telangana Board",
    "West Bengal Board", "Kerala Board", "NIOS",
]

KNOWN_QUALIFICATION_TYPES = [
    "B.Tech", "B.E.", "B.Sc", "BCA", "B.Com", "BA", "BBA",
    "M.Tech", "M.E.", "M.Sc", "MCA", "M.Com", "MA", "MBA",
    "PhD", "Diploma", "ITI",
]

# Work experience domains
WORK_DOMAINS = [
    "IT", "Non-IT", "Government", "Startup",
    "Freelance", "Education", "Healthcare",
    "Finance", "Manufacturing", "Other",
]

EMPLOYMENT_TYPES = [
    "Full-time", "Part-time", "Internship",
    "Contract", "Freelance",
]

# =============================================================================
# INTELLIGENCE LAYER — Risk Scoring Weights
# =============================================================================

RISK_WEIGHTS = {
    "education_gaps": 15,       # % weight for total education gap
    "backlogs": 20,             # % weight for backlog count
    "score_trend": 15,          # % weight for score improvement/decline
    "work_relevance": 15,       # % weight for IT/relevant domain experience
    "career_gaps": 10,          # % weight for unemployment gaps
    "domain_switches": 10,      # % weight for unrelated domain transitions
    "completeness": 15,         # % weight for data completeness
}

# Maximum penalty values (for normalizing each factor to 0-100 sub-score)
RISK_MAX_EDUCATION_GAP = 48     # months — beyond this = max penalty
RISK_MAX_BACKLOGS = 10          # count — beyond this = max penalty
RISK_MAX_CAREER_GAP = 24        # months — beyond this = max penalty
RISK_MAX_DOMAIN_SWITCHES = 5    # count — beyond this = max penalty

# =============================================================================
# RATIONALE VALIDATION — For soft rule exception overrides
# =============================================================================

RULE_RATIONALE_MIN_LENGTH = 30
RULE_RATIONALE_REQUIRED_KEYWORDS = [
    "approved by",
    "special case",
    "documentation pending",
    "waiver granted",
]

# =============================================================================
# EXCEPTION FLAGGING
# =============================================================================

RULE_MAX_EXCEPTIONS_BEFORE_FLAG = 2
