"""
AdmitGuard v2 — Data Quality Scorer
Computes a 0-100 data quality score based on completeness and consistency.
"""


def compute_data_quality(candidate_data, education_entries=None,
                         work_entries=None, tier2_flags=None):
    """
    Compute a data quality score (0-100).

    Factors:
      - Completeness (60%): % of expected fields filled
      - Consistency (40%): fewer flags = higher consistency

    Returns: {"score": float, "breakdown": {"completeness": float, "consistency": float}}
    """
    education_entries = education_entries or []
    work_entries = work_entries or []
    tier2_flags = tier2_flags or []

    # --- Completeness (60 points max) ---
    total_fields = 0
    filled_fields = 0

    # Core candidate fields
    core = ["full_name", "email", "phone", "date_of_birth", "aadhaar", "education_path"]
    for f in core:
        total_fields += 1
        if candidate_data.get(f) and str(candidate_data[f]).strip():
            filled_fields += 1

    # Education fields
    edu_fields = ["level", "board_university", "year_of_passing", "score", "stream"]
    for entry in education_entries:
        for f in edu_fields:
            total_fields += 1
            val = entry.get(f)
            if val is not None and str(val).strip():
                filled_fields += 1

    # Work fields
    work_fields = ["company_name", "designation", "domain", "start_date", "skills"]
    for entry in work_entries:
        for f in work_fields:
            total_fields += 1
            val = entry.get(f)
            if val is not None and str(val).strip() and val != "[]":
                filled_fields += 1

    completeness = (filled_fields / max(total_fields, 1)) * 100

    # --- Consistency (40 points max) ---
    # Fewer flags = higher consistency
    flag_count = len(tier2_flags)
    if flag_count == 0:
        consistency = 100
    elif flag_count <= 2:
        consistency = 70
    elif flag_count <= 4:
        consistency = 40
    else:
        consistency = 10

    # Weighted total
    score = (completeness * 0.6) + (consistency * 0.4)
    score = round(min(100, max(0, score)), 1)

    return {
        "score": score,
        "breakdown": {
            "completeness": round(completeness, 1),
            "consistency": consistency,
        },
    }
