# AdmitGuard v2 — Implementation Tasks

## Phase 1: Foundation & Architecture
- [ ] Create new database schema (education_entries, work_entries, enriched candidates table)
- [ ] Create `.env` config system (replace hardcoded secrets)
- [ ] Update [rules_config.py](file:///D:/IITGn/Projects/Week1/admitguard-yash-parmar/src/backend/rules_config.py) with v2 validation tiers

## Phase 2: Education Pathway Module (FR-1)
- [ ] Build education pathway validators (Path A/B/C logic)
- [ ] Create education entry model + CRUD
- [ ] Build dynamic frontend education form (adapts to path selection)
- [ ] Implement chronological ordering + score normalization

## Phase 3: Work Experience Module (FR-2)
- [ ] Create work experience model + CRUD
- [ ] Build work experience validators (dates, overlaps, gaps)
- [ ] Build frontend work experience form (add/remove entries, tag input)
- [ ] Auto-compute derived fields (total exp, domain-relevant exp, gap detection)

## Phase 4: Validation Engine Overhaul (FR-3)
- [ ] Implement Tier 1 (HARD REJECT) rules — server-side only
- [ ] Implement Tier 2 (SOFT FLAG) rules — save + flag logic
- [ ] Implement Tier 3 (ENRICHMENT) — computed metadata
- [ ] Remove offer letter logic, add application completeness scoring

## Phase 5: Intelligence Layer (FR-4)
- [ ] Implement Applicant Risk Scoring (0-100 weighted score)
- [ ] Implement Auto-Categorization ("Strong Fit" / "Needs Review" / "Weak Fit")
- [ ] Display risk score + category on confirmation screen
- [ ] Compute Data Quality Score per application

## Phase 6: Google Sheets Integration (FR-5)
- [ ] Set up Google Sheets API via service account (gspread)
- [ ] Auto-sync every validated submission to shared Google Sheet
- [ ] Include all captured + derived + intelligence fields
- [ ] Create summary/analytics sheet (bonus)

## Phase 7: Frontend Rebuild
- [ ] Redesign main form (multi-step, contextual sections)
- [ ] Build education pathway dynamic UI
- [ ] Build work experience dynamic UI
- [ ] Add loading states, mobile responsiveness, error handling
- [ ] Build submission confirmation/summary screen with risk score
- [ ] Update admin panel for new data model

## Phase 8: Deployment & Documentation
- [ ] Deploy to Render (backend) or Vercel (full stack)
- [ ] Update README with architecture, setup, live URL, screenshots
- [ ] Update sprint-log.md
- [ ] Clean up repo structure
