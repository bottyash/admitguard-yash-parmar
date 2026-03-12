"""
AdmitGuard v2 — Work Experience Validators
Per-entry validation, date logic, overlap detection,
and auto-computed derived fields (total exp, gaps, domain relevance).
"""

from datetime import datetime, date
import rules_config


# =============================================================================
# PER-ENTRY VALIDATION
# =============================================================================

def validate_work_entry(entry, index=0):
    """
    Validate a single work experience entry.
    Returns: {"valid": bool, "errors": {field: message}}
    """
    errors = {}

    # Company name
    company = (entry.get("company_name") or "").strip()
    if not company:
        errors["company_name"] = "Company name is required."
    elif len(company) < 2:
        errors["company_name"] = "Company name must be at least 2 characters."

    # Designation
    designation = (entry.get("designation") or "").strip()
    if not designation:
        errors["designation"] = "Designation/role is required."

    # Domain
    domain = (entry.get("domain") or "Other").strip()
    if domain not in rules_config.WORK_DOMAINS:
        errors["domain"] = (
            f"Invalid domain '{domain}'. "
            f"Must be one of: {', '.join(rules_config.WORK_DOMAINS)}"
        )

    # Employment type
    emp_type = (entry.get("employment_type") or "Full-time").strip()
    if emp_type not in rules_config.EMPLOYMENT_TYPES:
        errors["employment_type"] = (
            f"Invalid type '{emp_type}'. "
            f"Must be one of: {', '.join(rules_config.EMPLOYMENT_TYPES)}"
        )

    # Start date (required)
    start_str = (entry.get("start_date") or "").strip()
    start_date = _parse_date(start_str)
    if not start_str:
        errors["start_date"] = "Start date is required."
    elif start_date is None:
        errors["start_date"] = "Invalid date format. Use YYYY-MM-DD."
    elif start_date > date.today():
        errors["start_date"] = "Start date cannot be in the future."

    # End date (optional — empty means currently working)
    end_str = (entry.get("end_date") or "").strip()
    end_date = None
    if end_str:
        end_date = _parse_date(end_str)
        if end_date is None:
            errors["end_date"] = "Invalid date format. Use YYYY-MM-DD."
        elif end_date > date.today():
            errors["end_date"] = "End date cannot be in the future."
        elif start_date and end_date and end_date < start_date:
            errors["end_date"] = "End date cannot be before start date."

    # Skills (optional, should be list)
    skills = entry.get("skills", [])
    if isinstance(skills, str):
        # Accept comma-separated string
        skills = [s.strip() for s in skills.split(",") if s.strip()]
        entry["skills"] = skills

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "entry_index": index,
    }


# =============================================================================
# OVERLAP DETECTION
# =============================================================================

def detect_overlaps(entries):
    """
    Detect overlapping work periods.
    Returns: list of overlap warnings (not errors — concurrent jobs are allowed).
    """
    warnings = []
    dated_entries = []

    for i, entry in enumerate(entries):
        start = _parse_date(entry.get("start_date", ""))
        end = _parse_date(entry.get("end_date", "")) or date.today()
        if start:
            dated_entries.append((i, entry, start, end))

    # Sort by start date
    dated_entries.sort(key=lambda x: x[2])

    for i in range(len(dated_entries) - 1):
        idx_a, entry_a, start_a, end_a = dated_entries[i]
        idx_b, entry_b, start_b, end_b = dated_entries[i + 1]

        if start_b < end_a:
            overlap_months = _months_between(start_b, min(end_a, end_b))
            warnings.append(
                f"Overlap: {entry_a.get('company_name', '?')} "
                f"and {entry_b.get('company_name', '?')} "
                f"overlap by ~{overlap_months} month(s)."
            )

    return warnings


# =============================================================================
# DERIVED FIELDS
# =============================================================================

def compute_derived_fields(entries):
    """
    Compute derived fields for a set of work entries:
      - tenure_months per entry
      - total_experience_months
      - domain_relevant_months (IT domain)
      - career_gaps (list of gaps between jobs)
      - total_gap_months
      - domain_transitions (count of unrelated domain switches)
      - employment_status ("Currently Working" or "Not Working")
      - unique_domains

    Returns: dict of computed values + modifies entries in-place with tenure_months
    """
    total_exp = 0
    domain_relevant = 0
    gaps = []
    domains_in_order = []
    is_currently_working = False

    # Parse and sort by start date
    parsed = []
    for entry in entries:
        start = _parse_date(entry.get("start_date", ""))
        end_str = (entry.get("end_date") or "").strip()
        end = _parse_date(end_str) if end_str else None
        domain = (entry.get("domain") or "Other").strip()

        if start:
            actual_end = end or date.today()
            tenure = _months_between(start, actual_end)
            entry["tenure_months"] = tenure
            parsed.append((start, actual_end, end is None, domain, tenure))
            domains_in_order.append(domain)

            if end is None:
                is_currently_working = True
        else:
            entry["tenure_months"] = 0

    # Sort by start date
    parsed.sort(key=lambda x: x[0])

    for i, (start, end, is_current, domain, tenure) in enumerate(parsed):
        total_exp += tenure

        # Count IT/relevant domain experience
        if domain in ("IT", "Startup"):
            domain_relevant += tenure

        # Calculate gaps between consecutive jobs
        if i > 0:
            prev_end = parsed[i - 1][1]
            if start > prev_end:
                gap = _months_between(prev_end, start)
                if gap > 0:
                    gaps.append({
                        "gap_months": gap,
                        "from_date": prev_end.isoformat(),
                        "to_date": start.isoformat(),
                    })

    # Count domain transitions (non-adjacent domain changes)
    domain_transitions = 0
    for i in range(1, len(domains_in_order)):
        if domains_in_order[i] != domains_in_order[i - 1]:
            domain_transitions += 1

    total_gap_months = sum(g["gap_months"] for g in gaps)

    # Experience bucket
    experience_bucket = "Fresher"
    for bucket, (low, high) in rules_config.EXPERIENCE_BUCKETS.items():
        if low <= total_exp <= high:
            experience_bucket = bucket
            break

    return {
        "total_experience_months": total_exp,
        "domain_relevant_months": domain_relevant,
        "career_gaps": gaps,
        "total_gap_months": total_gap_months,
        "domain_transitions": domain_transitions,
        "employment_status": "Currently Working" if is_currently_working else "Not Working",
        "experience_bucket": experience_bucket,
        "unique_domains": list(set(domains_in_order)),
    }


# =============================================================================
# FULL WORK EXPERIENCE VALIDATION
# =============================================================================

def validate_all_work(entries):
    """
    Run all work experience validations:
      1. Per-entry validation
      2. Overlap detection
      3. Derived field computation

    Returns: {
        "valid": bool,
        "entry_errors": [{entry_index, errors}],
        "overlaps": [str],
        "derived": {total_experience_months, gaps, etc.},
        "entries": [...entries with tenure_months]
    }
    """
    entry_errors = []

    # 1. Per-entry validation
    for i, entry in enumerate(entries):
        result = validate_work_entry(entry, index=i)
        if not result["valid"]:
            entry_errors.append({
                "entry_index": i,
                "company": (entry.get("company_name") or "").strip(),
                "errors": result["errors"],
            })

    # 2. Overlap detection
    overlaps = detect_overlaps(entries)

    # 3. Derived fields
    derived = compute_derived_fields(entries)

    return {
        "valid": len(entry_errors) == 0,
        "entry_errors": entry_errors,
        "overlaps": overlaps,  # warnings, not blocking
        "derived": derived,
        "entries": entries,
    }


# =============================================================================
# HELPERS
# =============================================================================

def _parse_date(date_str):
    """Parse YYYY-MM-DD string to date object, return None on failure."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _months_between(d1, d2):
    """Calculate approximate months between two dates."""
    if not d1 or not d2:
        return 0
    delta = (d2.year - d1.year) * 12 + (d2.month - d1.month)
    return max(0, delta)
