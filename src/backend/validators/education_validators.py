"""
AdmitGuard v2 — Education Validators
Handles Indian education pathway enforcement (Path A/B/C),
chronological year validation, per-entry validation, and score normalization.
"""

from datetime import datetime
import rules_config


# =============================================================================
# PER-ENTRY VALIDATION
# =============================================================================

def validate_education_entry(entry, index=0):
    """
    Validate a single education entry.
    Returns: {"valid": bool, "errors": {field: message}}
    """
    errors = {}

    # Level is required and must be valid
    level = (entry.get("level") or "").strip()
    if not level:
        errors["level"] = "Education level is required."
    elif level not in rules_config.VALID_EDUCATION_LEVELS:
        errors["level"] = (
            f"Invalid level '{level}'. "
            f"Must be one of: {', '.join(rules_config.VALID_EDUCATION_LEVELS)}"
        )

    # Board/University is required
    board = (entry.get("board_university") or "").strip()
    if not board:
        errors["board_university"] = "Board/University is required."
    elif len(board) < 2:
        errors["board_university"] = "Board/University must be at least 2 characters."

    # Stream is required for 12th and above
    stream = (entry.get("stream") or "").strip()
    if level in ("12th", "Diploma", "ITI", "UG", "PG", "PhD") and not stream:
        errors["stream"] = f"Stream/Specialization is required for {level}."

    # Year of passing
    year = entry.get("year_of_passing")
    if year is not None:
        try:
            year = int(year)
            current_year = datetime.now().year
            if year > current_year:
                errors["year_of_passing"] = (
                    f"Year of passing ({year}) cannot be in the future."
                )
            elif year < 1970:
                errors["year_of_passing"] = "Year of passing seems too old."
        except (ValueError, TypeError):
            errors["year_of_passing"] = "Year of passing must be a valid number."
    else:
        errors["year_of_passing"] = "Year of passing is required."

    # Score validation
    score = entry.get("score")
    score_scale = (entry.get("score_scale") or "percentage").strip()

    if score is not None and score != "":
        try:
            score = float(score)
            if score < 0:
                errors["score"] = "Score cannot be negative."
            else:
                # Check max based on scale
                if score_scale == "percentage" and score > rules_config.RULE_SCORE_MAX_PERCENTAGE:
                    errors["score"] = f"Percentage cannot exceed {rules_config.RULE_SCORE_MAX_PERCENTAGE}."
                elif score_scale == "cgpa_10" and score > rules_config.RULE_SCORE_MAX_CGPA_10:
                    errors["score"] = f"CGPA (out of 10) cannot exceed {rules_config.RULE_SCORE_MAX_CGPA_10}."
                elif score_scale == "cgpa_4" and score > rules_config.RULE_SCORE_MAX_CGPA_4:
                    errors["score"] = f"CGPA (out of 4) cannot exceed {rules_config.RULE_SCORE_MAX_CGPA_4}."
        except (ValueError, TypeError):
            errors["score"] = "Score must be a valid number."
    else:
        errors["score"] = "Score is required."

    # Score scale validation
    if score_scale not in rules_config.SCORE_SCALES:
        errors["score_scale"] = (
            f"Invalid score scale. Must be one of: "
            f"{', '.join(rules_config.SCORE_SCALES.keys())}"
        )

    # Backlog count (only for UG/PG/PhD)
    backlog_count = entry.get("backlog_count", 0)
    if level in ("UG", "PG", "PhD"):
        try:
            backlog_count = int(backlog_count)
            if backlog_count < 0:
                errors["backlog_count"] = "Backlog count cannot be negative."
        except (ValueError, TypeError):
            errors["backlog_count"] = "Backlog count must be a valid number."

    # Gap months
    gap_months = entry.get("gap_months", 0)
    try:
        gap_months = int(gap_months)
        if gap_months < 0:
            errors["gap_months"] = "Gap cannot be negative."
    except (ValueError, TypeError):
        errors["gap_months"] = "Gap months must be a valid number."

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "entry_index": index,
    }


# =============================================================================
# PATH VALIDATION
# =============================================================================

def validate_education_path(entries, path):
    """
    Validate that education entries match the selected pathway (A/B/C).
    Checks:
      1. All required levels are present
      2. No invalid levels for this path
      3. 10th is always mandatory

    Returns: {"valid": bool, "errors": [str], "warnings": [str]}
    """
    errors = []
    warnings = []

    if path not in rules_config.EDUCATION_PATHS:
        errors.append(f"Invalid education path '{path}'. Must be A, B, or C.")
        return {"valid": False, "errors": errors, "warnings": warnings}

    path_config = rules_config.EDUCATION_PATHS[path]
    required_levels = path_config["required"]
    optional_levels = path_config["optional"]
    all_allowed = set(required_levels + optional_levels)

    # Get levels present in entries
    present_levels = set()
    for entry in entries:
        level = (entry.get("level") or "").strip()
        if level:
            present_levels.add(level)

    # Check 10th is always present
    if "10th" not in present_levels:
        errors.append("10th standard is mandatory for all education paths.")

    # Check all required levels are present
    for level in required_levels:
        if level not in present_levels:
            errors.append(
                f"Path {path} ({path_config['name']}) requires {level}."
            )

    # Warn about levels not in this path
    for level in present_levels:
        if level not in all_allowed:
            warnings.append(
                f"{level} is not standard for Path {path}. "
                f"Expected: {', '.join(required_levels)}."
            )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


# =============================================================================
# CHRONOLOGICAL VALIDATION
# =============================================================================

def validate_chronological_order(entries):
    """
    Validate that years of passing are in chronological order
    based on education level hierarchy.

    Returns: {"valid": bool, "errors": [str]}
    """
    errors = []

    # Sort entries by level order
    level_order = rules_config.EDUCATION_LEVEL_ORDER
    sorted_entries = sorted(
        entries,
        key=lambda e: level_order.get((e.get("level") or "").strip(), 99)
    )

    prev_year = None
    prev_level = None

    for entry in sorted_entries:
        level = (entry.get("level") or "").strip()
        year = entry.get("year_of_passing")

        if year is None:
            continue

        try:
            year = int(year)
        except (ValueError, TypeError):
            continue

        if prev_year is not None and prev_level is not None:
            # Same tier levels (12th and ITI are both tier 2) can be same year
            prev_order = level_order.get(prev_level, 99)
            curr_order = level_order.get(level, 99)

            if curr_order > prev_order and year < prev_year:
                errors.append(
                    f"Chronological error: {level} ({year}) cannot be "
                    f"before {prev_level} ({prev_year})."
                )
            elif curr_order == prev_order and year < prev_year - 1:
                # Same tier: allow 1 year tolerance
                errors.append(
                    f"Chronological error: {level} ({year}) and "
                    f"{prev_level} ({prev_year}) seem inconsistent."
                )

        prev_year = year
        prev_level = level

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }


# =============================================================================
# SCORE NORMALIZATION
# =============================================================================

def normalize_score(score, score_scale):
    """
    Convert any score scale to percentage equivalent.
    - percentage: return as-is
    - cgpa_10: multiply by 9.5 (standard approximation)
    - cgpa_4: multiply by 25
    - grade: return None (manual mapping needed)

    Returns: float (normalized percentage) or None
    """
    if score is None:
        return None

    try:
        score = float(score)
    except (ValueError, TypeError):
        return None

    scale_config = rules_config.SCORE_SCALES.get(score_scale)
    if not scale_config:
        return None

    converter = scale_config.get("to_percentage")
    if converter is None:
        return None  # Grade scale — can't auto-convert

    return round(converter(score), 2)


def normalize_all_entries(entries):
    """
    Add normalized_score to each education entry.
    Returns the entries with normalized_score populated.
    """
    for entry in entries:
        score = entry.get("score")
        scale = entry.get("score_scale", "percentage")
        entry["normalized_score"] = normalize_score(score, scale) or 0
    return entries


# =============================================================================
# GAP CALCULATION
# =============================================================================

def calculate_education_gaps(entries):
    """
    Calculate gap in months between consecutive education levels.
    Sets gap_months on each entry (gap BEFORE this entry).
    Returns total gap months.
    """
    level_order = rules_config.EDUCATION_LEVEL_ORDER
    sorted_entries = sorted(
        entries,
        key=lambda e: level_order.get((e.get("level") or "").strip(), 99)
    )

    total_gap = 0
    prev_year = None

    for entry in sorted_entries:
        year = entry.get("year_of_passing")
        if year is None:
            entry["gap_months"] = 0
            continue

        try:
            year = int(year)
        except (ValueError, TypeError):
            entry["gap_months"] = 0
            continue

        if prev_year is not None:
            gap_years = year - prev_year
            # Typical gap: subtract expected duration (approx 2-4 years)
            # Simple heuristic: if gap > 1 year beyond expected, count the extra
            expected_gap = 2  # Most levels take ~2 years
            actual_gap_months = max(0, (gap_years - expected_gap) * 12)
            entry["gap_months"] = actual_gap_months
            total_gap += actual_gap_months
        else:
            entry["gap_months"] = 0

        prev_year = year

    return total_gap


# =============================================================================
# FULL EDUCATION VALIDATION (combines all checks)
# =============================================================================

def validate_all_education(entries, path):
    """
    Run all education validations:
      1. Per-entry validation
      2. Path validation
      3. Chronological order
      4. Score normalization
      5. Gap calculation

    Returns: {
        "valid": bool,
        "entry_errors": [{entry_index, errors}],
        "path_errors": [str],
        "chronological_errors": [str],
        "warnings": [str],
        "total_gap_months": int,
        "total_backlogs": int,
        "entries": [...entries with normalized_score and gap_months]
    }
    """
    entry_errors = []
    all_warnings = []

    # 1. Per-entry validation
    for i, entry in enumerate(entries):
        result = validate_education_entry(entry, index=i)
        if not result["valid"]:
            entry_errors.append({
                "entry_index": i,
                "level": (entry.get("level") or "").strip(),
                "errors": result["errors"],
            })

    # 2. Path validation
    path_result = validate_education_path(entries, path)
    path_errors = path_result["errors"]
    all_warnings.extend(path_result.get("warnings", []))

    # 3. Chronological order
    chrono_result = validate_chronological_order(entries)
    chrono_errors = chrono_result["errors"]

    # 4. Score normalization
    entries = normalize_all_entries(entries)

    # 5. Gap calculation
    total_gap = calculate_education_gaps(entries)

    # 6. Total backlogs
    total_backlogs = 0
    for entry in entries:
        try:
            total_backlogs += int(entry.get("backlog_count", 0))
        except (ValueError, TypeError):
            pass

    # Overall validity (entry errors or path errors = invalid)
    is_valid = len(entry_errors) == 0 and len(path_errors) == 0 and len(chrono_errors) == 0

    return {
        "valid": is_valid,
        "entry_errors": entry_errors,
        "path_errors": path_errors,
        "chronological_errors": chrono_errors,
        "warnings": all_warnings,
        "total_gap_months": total_gap,
        "total_backlogs": total_backlogs,
        "entries": entries,
    }
