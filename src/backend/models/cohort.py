"""
AdmitGuard v2 — Cohort Model
Manages intake cohorts with per-cohort rule overrides.
Admin can create cohorts and tweak validation params per cohort via UI.
"""

import uuid
import json
from datetime import datetime
from db import get_connection
import rules_config


def create_cohort(name, description=""):
    """Create a new intake cohort. Returns the created cohort dict."""
    cohort_id = str(uuid.uuid4())
    now = datetime.now().isoformat()

    conn = get_connection()
    with conn:
        conn.execute("""
            INSERT INTO cohorts (id, name, description, is_active, created_at)
            VALUES (?, ?, ?, 1, ?)
        """, (cohort_id, name.strip(), description.strip(), now))

        # Audit log
        conn.execute("""
            INSERT INTO audit_log (id, candidate_id, candidate_name,
                candidate_email, action, details, cohort_id, timestamp)
            VALUES (?, '', '', '', 'COHORT_CREATE', ?, ?, ?)
        """, (
            str(uuid.uuid4()), json.dumps({"name": name}), cohort_id, now,
        ))
    conn.close()

    return get_cohort_by_id(cohort_id)


def get_all_cohorts():
    """Return all cohorts as list of dicts."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM cohorts ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [_cohort_to_dict(r) for r in rows]


def get_cohort_by_id(cohort_id):
    """Return a single cohort with its params."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM cohorts WHERE id = ?", (cohort_id,)
    ).fetchone()
    if not row:
        conn.close()
        return None

    cohort = _cohort_to_dict(row)

    # Fetch params
    param_rows = conn.execute(
        "SELECT param_name, param_value FROM cohort_params WHERE cohort_id = ?",
        (cohort_id,)
    ).fetchall()
    cohort["params"] = {r["param_name"]: r["param_value"] for r in param_rows}

    conn.close()
    return cohort


def update_cohort(cohort_id, name=None, description=None, is_active=None):
    """Update cohort metadata. Returns updated cohort or None."""
    updates = []
    values = []
    if name is not None:
        updates.append("name = ?")
        values.append(name.strip())
    if description is not None:
        updates.append("description = ?")
        values.append(description.strip())
    if is_active is not None:
        updates.append("is_active = ?")
        values.append(1 if is_active else 0)

    if not updates:
        return get_cohort_by_id(cohort_id)

    values.append(cohort_id)
    sql = f"UPDATE cohorts SET {', '.join(updates)} WHERE id = ?"

    conn = get_connection()
    with conn:
        cursor = conn.execute(sql, values)
        if cursor.rowcount == 0:
            conn.close()
            return None
    conn.close()
    return get_cohort_by_id(cohort_id)


def get_cohort_params(cohort_id):
    """Return dict of param overrides for a cohort."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT param_name, param_value FROM cohort_params WHERE cohort_id = ?",
        (cohort_id,)
    ).fetchall()
    conn.close()
    return {r["param_name"]: r["param_value"] for r in rows}


def update_cohort_params(cohort_id, params):
    """
    Upsert param overrides for a cohort.
    params: dict of {param_name: param_value}
    Returns the full updated params dict.
    """
    conn = get_connection()

    # Verify cohort exists
    cohort = conn.execute(
        "SELECT id FROM cohorts WHERE id = ?", (cohort_id,)
    ).fetchone()
    if not cohort:
        conn.close()
        return None

    with conn:
        for param_name, param_value in params.items():
            param_id = str(uuid.uuid4())
            # UPSERT: insert or replace on conflict
            conn.execute("""
                INSERT INTO cohort_params (id, cohort_id, param_name, param_value)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(cohort_id, param_name) DO UPDATE SET param_value = ?
            """, (param_id, cohort_id, param_name, str(param_value), str(param_value)))

        # Audit
        now = datetime.now().isoformat()
        conn.execute("""
            INSERT INTO audit_log (id, candidate_id, candidate_name,
                candidate_email, action, details, cohort_id, timestamp)
            VALUES (?, '', '', '', 'COHORT_PARAMS_UPDATE', ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            json.dumps({"updated_params": list(params.keys())}),
            cohort_id, now,
        ))

    conn.close()
    return get_cohort_params(cohort_id)


def delete_cohort_param(cohort_id, param_name):
    """Delete a single param override (reverts to default)."""
    conn = get_connection()
    with conn:
        conn.execute(
            "DELETE FROM cohort_params WHERE cohort_id = ? AND param_name = ?",
            (cohort_id, param_name)
        )
    conn.close()


def get_effective_rules(cohort_id=None):
    """
    Merge default rules_config values with cohort-specific overrides.
    Returns a dict of all rule values with overrides applied.

    Admin can override any numeric/string rule from rules_config.py.
    """
    # Start with defaults from rules_config
    defaults = {
        # Tier 1
        "age_minimum": rules_config.RULE_AGE_MINIMUM,
        "phone_length": rules_config.RULE_PHONE_LENGTH,
        "aadhaar_length": rules_config.RULE_AADHAAR_LENGTH,
        "name_min_length": rules_config.RULE_NAME_MIN_LENGTH,
        "score_max_percentage": rules_config.RULE_SCORE_MAX_PERCENTAGE,
        "score_max_cgpa_10": rules_config.RULE_SCORE_MAX_CGPA_10,
        "score_max_cgpa_4": rules_config.RULE_SCORE_MAX_CGPA_4,

        # Tier 2
        "max_education_gap_months": rules_config.RULE_MAX_EDUCATION_GAP_MONTHS,
        "max_career_gap_months": rules_config.RULE_MAX_CAREER_GAP_MONTHS,
        "max_domain_transitions": rules_config.RULE_MAX_DOMAIN_TRANSITIONS,
        "years_since_education_no_work": rules_config.RULE_YEARS_SINCE_EDUCATION_NO_WORK,
        "score_threshold_percentage": rules_config.RULE_SCORE_THRESHOLD_PERCENTAGE,
        "score_threshold_cgpa_10": rules_config.RULE_SCORE_THRESHOLD_CGPA_10,
        "score_threshold_cgpa_4": rules_config.RULE_SCORE_THRESHOLD_CGPA_4,
        "screening_score_min": rules_config.RULE_SCREENING_SCORE_MIN,

        # Tier 3
        "category_strong_fit_max": rules_config.CATEGORY_STRONG_FIT_MAX,
        "category_needs_review_max": rules_config.CATEGORY_NEEDS_REVIEW_MAX,

        # Exception
        "max_exceptions_before_flag": rules_config.RULE_MAX_EXCEPTIONS_BEFORE_FLAG,
        "rationale_min_length": rules_config.RULE_RATIONALE_MIN_LENGTH,
    }

    if not cohort_id:
        return defaults

    # Apply cohort overrides
    overrides = get_cohort_params(cohort_id)
    for param_name, param_value in overrides.items():
        if param_name in defaults:
            # Type-cast to match the default's type
            default_val = defaults[param_name]
            try:
                if isinstance(default_val, float):
                    defaults[param_name] = float(param_value)
                elif isinstance(default_val, int):
                    defaults[param_name] = int(param_value)
                else:
                    defaults[param_name] = param_value
            except (ValueError, TypeError):
                pass  # Keep default if conversion fails

    return defaults


# =============================================================================
# Helpers
# =============================================================================

# Params that admin can tweak per cohort (for UI rendering)
TWEAKABLE_PARAMS = [
    {"name": "age_minimum", "label": "Minimum Age", "type": "number", "min": 16, "max": 25, "step": 1},
    {"name": "max_education_gap_months", "label": "Max Education Gap (months)", "type": "number", "min": 6, "max": 60, "step": 6},
    {"name": "max_career_gap_months", "label": "Max Career Gap (months)", "type": "number", "min": 3, "max": 24, "step": 3},
    {"name": "max_domain_transitions", "label": "Max Domain Transitions", "type": "number", "min": 1, "max": 10, "step": 1},
    {"name": "years_since_education_no_work", "label": "Max Years Since Education (no work)", "type": "number", "min": 1, "max": 10, "step": 1},
    {"name": "score_threshold_percentage", "label": "Min Score Threshold (%)", "type": "number", "min": 30, "max": 90, "step": 5},
    {"name": "screening_score_min", "label": "Min Screening Score", "type": "number", "min": 20, "max": 80, "step": 5},
    {"name": "category_strong_fit_max", "label": "Strong Fit Max Risk Score", "type": "number", "min": 10, "max": 50, "step": 5},
    {"name": "category_needs_review_max", "label": "Needs Review Max Risk Score", "type": "number", "min": 30, "max": 80, "step": 5},
    {"name": "max_exceptions_before_flag", "label": "Max Exceptions Before Flag", "type": "number", "min": 1, "max": 5, "step": 1},
]


def get_tweakable_params():
    """Return list of params that admin can adjust, with metadata for UI."""
    return TWEAKABLE_PARAMS


def _cohort_to_dict(row):
    """Convert a sqlite3.Row to dict."""
    if not row:
        return None
    d = dict(row)
    d["is_active"] = bool(d.get("is_active", 1))
    return d
