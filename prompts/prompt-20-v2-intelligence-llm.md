# Prompt 20 — v2 Intelligence Layer + LLM Integration (FR-4)

## R.I.C.E. Framework

### Role
You are a backend engineer building the intelligence layer for AdmitGuard v2 — risk scoring, auto-categorization, data quality measurement, and 8 LLM-powered features via local Ollama.

### Intent
Every submission is now scored, categorized, and narrated automatically. The LLM provides soft doc verification, form assistance, email drafting, NL queries, and profile summaries — all with graceful fallback if Ollama is unavailable.

### Constraints
- **Risk scoring**: weighted 0-100 based on 7 factors (education gaps 15%, backlogs 20%, score trend 15%, work relevance 15%, career gaps 10%, domain switches 10%, completeness 15%).
- **Categorization**: Strong Fit (≤30), Needs Review (31-60), Weak Fit (>60). Thresholds overridable per cohort.
- **LLM never blocks**: All LLM calls wrapped in try/except. `is_available()` checks Ollama before calling. Fallback strings returned if unavailable.
- **`_llm_json_call`** handles markdown code fence stripping for robust JSON parsing.
- **11 API endpoints** exposed via `routes/llm_routes.py` blueprint.

### Changes Made
| File | Change |
|------|--------|
| `intelligence/__init__.py` | NEW — package init |
| `intelligence/risk_scorer.py` | NEW — 7-factor weighted risk scoring |
| `intelligence/categorizer.py` | NEW — 3-bucket categorization with confidence |
| `intelligence/data_quality.py` | NEW — completeness (60%) + consistency (40%) scoring |
| `intelligence/llm_assistant.py` | NEW — 8 LLM features via Ollama with graceful fallback |
| `routes/llm_routes.py` | NEW — 11 API endpoints for LLM features |
| `routes/candidates.py` | Updated — real risk scoring, categorization, data quality, narration in submission pipeline |
| `app.py` | Updated — LLM blueprint registered, health shows llm_available |

### Expected Outcome (Verification)
1. ✅ Submission with education+work → risk_score 23.2/100, category "Strong Fit"
2. ✅ Dashboard: `avg_risk_score: 23.2`, `category_distribution: {"Strong Fit": 1}`
3. ✅ LLM status: `available: false` (Ollama not running) — graceful degradation
4. ✅ Submission succeeds even without LLM — fallback narration, llm_flags=0
5. ✅ 11 LLM endpoints registered and responding
