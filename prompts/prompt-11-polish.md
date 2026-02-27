# Prompt 11 — Audit Search & UI Polish

## R.I.C.E. Framework

### Role
You are a frontend engineer polishing the AdmitGuard **Audit Log** for high-volume data entry.

### Intent
Enhance the Audit Log tab in `src/frontend/app.js` and `styles.css` with a live-search bar, a candidate count badge, and a dedicated export control bar. Also, implement a keyboard shortcut for faster form submission.

### Constraints
- **Live Search**: Filter the already-fetched `_lastLog` cache client-side by name or email. Update the table as the user types.
- **Entry Count**: Show a label like "12 entries" or "1 entry" that updates based on filters/search.
- **Export Bar**: Add a stylized container above the audit table with "⬇ CSV" and "⬇ JSON" download buttons.
- **Keyboard Shortcut**: `Ctrl + Enter` (or `Cmd + Enter`) anywhere on the page triggers the "Submit" action.
- **CSS Polish**: Add a custom themed scrollbar for the audit table wrapper. Fix the `-webkit-appearance` CSS lint by adding the standard `appearance` property.

### UI Components (HTML/CSS)
```html
<div class="audit-toolbar">
  <input id="audit-search" placeholder="🔍 Search...">
  <span id="audit-count">0 entries</span>
</div>
<div class="export-bar">
  <button onclick="downloadCSV()">⬇ CSV</button>
  <button onclick="downloadJSON()">⬇ JSON</button>
</div>
```

### Verification
1. Type a name in search → Table should filter instantly.
2. Press `Ctrl+Enter` → Spinner should appear on Submit button.
3. Check browser console → No "appearance" property warnings.
