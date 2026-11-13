# Chapter 5 — Input / Output Design

**Project:** NivasSetu  **Version:** 1.0

---

## 5.1 Design Principles

- **Mobile-first:** forms stacked vertically, full-width on small screens
- **Labels always visible:** no placeholder-only labels (accessibility)
- **Inline validation:** server-side errors rendered next to each field
- **Action feedback:** HTMX success/error toasts on every POST
- **Confirmation dialogs:** shown before destructive actions (close ticket, delete)

---

## 5.2 Input Form Designs

### Form 1 — Login (`/accounts/login/`)

| # | Field | HTML Type | Required | Validation | Notes |
|---|-------|-----------|----------|-----------|-------|
| 1 | Username | text | Yes | Non-empty, max 150 chars | Auto-focused on page load |
| 2 | Password | password | Yes | Non-empty | Masked input |
| — | Sign In | submit | — | — | Redirects to role dashboard |
| — | Demo buttons | button | — | — | Auto-fills secretary / resident / staff credentials |

**Error messages:**
- "Please enter a correct username and password."
- Fields highlighted with red border on failure.

---

### Form 2 — Create Complaint (`/complaints/create/`)

| # | Field | HTML Type | Required | Validation | Notes |
|---|-------|-----------|----------|-----------|-------|
| 1 | Category | select | Yes | Must select from list | Populated from ComplaintCategory |
| 2 | Priority | select | Yes | One of: Low / Medium / High / Critical | Colour-coded badge preview |
| 3 | Description | textarea | Yes | Min 20 chars, max 2000 | Character counter hint |
| 4 | Photo | file | No | JPEG/PNG, max 5 MB | Preview thumbnail on select |
| — | Submit | submit | — | — | Redirects to complaint detail |

**Server-side rules:**
- Resident must have a ResidentProfile (linked flat) before they can file.
- If ComplaintCategory list is empty, an informational message is shown.

---

### Form 3 — Update Complaint Status (Complaint Detail Page)

| # | Field | HTML Type | Required | Validation | Notes |
|---|-------|-----------|----------|-----------|-------|
| 1 | New Status | select | Yes | Valid next state from workflow | Only allowed transitions shown |
| 2 | Remark | textarea | No | Max 500 chars | Encouraged for transparency |
| — | Update | submit | — | — | HTMX partial — updates timeline in-place |

**Allowed transitions by role:**
| Current | Secretary can go to | Staff can go to | Resident can go to |
|---------|--------------------|-----------------|--------------------|
| OPEN | ASSIGNED, CLOSED | — | — |
| ASSIGNED | IN_PROGRESS, CLOSED | IN_PROGRESS | — |
| IN_PROGRESS | RESOLVED, CLOSED | RESOLVED | — |
| RESOLVED | CLOSED | CLOSED | OPEN (Reopen, within 7 days) |
| CLOSED | — | — | — |

---

### Form 4 — Assign Staff (`/complaints/<id>/assign/`)

| # | Field | HTML Type | Required | Validation | Notes |
|---|-------|-----------|----------|-----------|-------|
| 1 | Staff Member | select | Yes | Must select active staff | Shows trade in parentheses |
| — | Assign | submit | — | — | HTMX — updates assignment panel |

**Visible only to:** Secretary  
**Result:** Status changes to ASSIGNED; history entry created.

---

### Form 5 — Add Comment (`/complaints/<id>/comment/`)

| # | Field | HTML Type | Required | Validation | Notes |
|---|-------|-----------|----------|-----------|-------|
| 1 | Comment | textarea | Yes | Min 1 char, max 1000 | Appears in timeline below |
| — | Post | submit | — | — | HTMX — appends comment to thread |

**Visible to:** Secretary, Resident (own complaints), Staff (assigned complaints)

---

### Form 6 — Submit Feedback (`/complaints/<id>/feedback/`)

| # | Field | HTML Type | Required | Validation | Notes |
|---|-------|-----------|----------|-----------|-------|
| 1 | Rating | radio (1–5) | Yes | Integer 1 to 5 | Star icons rendered via CSS |
| 2 | Comment | textarea | No | Max 500 chars | Optional text |
| — | Submit | submit | — | — | One-time form; hidden after submission |

**Condition:** Only shown when status = RESOLVED and no feedback yet given.

---

### Form 7 — Create Notice (`/notices/create/`)

| # | Field | HTML Type | Required | Validation | Notes |
|---|-------|-----------|----------|-----------|-------|
| 1 | Title | text | Yes | Max 200 chars | |
| 2 | Body | textarea | Yes | Min 10 chars | Markdown-aware display |
| 3 | Category | select | Yes | GENERAL/MAINTENANCE/FINANCE/EMERGENCY | |
| 4 | Pin this notice | checkbox | No | — | Floated to top of list |
| 5 | Expires on | date | No | Must be future date if provided | |
| — | Publish | submit | — | — | Redirects to notice list |

---

### Form 8 — Generate Dues (`/dues/generate/`)

| # | Field | HTML Type | Required | Validation | Notes |
|---|-------|-----------|----------|-----------|-------|
| 1 | Maintenance Plan | select | Yes | Active plans | Shows base charge + rate |
| 2 | Month | select | Yes | 1–12 | |
| 3 | Year | number | Yes | 2020–2030 | |
| — | Generate | submit | — | — | Prevents duplicate (unique month+year+plan) |

**Result:** One DuesRecord per flat, amount = base_charge + rate × sq_ft.

---

### Form 9 — Record Payment (`/dues/pay/<id>/`)

| # | Field | HTML Type | Required | Validation | Notes |
|---|-------|-----------|----------|-----------|-------|
| 1 | Amount | number | Yes | > 0, ≤ outstanding balance | Decimal, 2 places |
| 2 | Mode | select | Yes | Cash / UPI / Cheque | |
| 3 | Reference | text | No | Max 100 chars | Required hint shown for UPI/Cheque |
| 4 | Paid On | date | Yes | ≤ today | |
| — | Record Payment | submit | — | — | Auto-generates receipt number |

---

## 5.3 Output Screen Descriptions

### Output 1 — Secretary Dashboard (`/dashboard/`)

**Summary cards row (top):**
| Card | Value shown |
|------|------------|
| Open Tickets | Count of OPEN + ASSIGNED complaints |
| Overdue | Count where is_overdue = True |
| Resolved This Month | Count resolved in current calendar month |
| Dues Pending | Total (amount_due − amount_paid) in ₹ |

**Below the cards:**
- Table: 10 most recently updated complaints (ticket #, category, flat, status badge, priority badge, assigned to)
- Table: 5 latest notices with acknowledgement count

---

### Output 2 — Resident Dashboard (`/dashboard/`)

- 3 cards: My Open Tickets, My Resolved Tickets, Pending Dues (₹)
- Table: resident's last 5 complaints with status badge and "View" link
- Section: unacknowledged notices (with "Mark as Read" HTMX button)

---

### Output 3 — Staff Dashboard (`/dashboard/`)

- 2 cards: Assigned to Me (open), Overdue
- Table: all assigned complaints with priority and SLA deadline; overdue rows highlighted in red

---

### Output 4 — Complaint Detail Page (`/complaints/<id>/`)

**Header:**
- Ticket number, category, priority badge, status badge, SLA deadline, overdue warning (if applicable)

**Timeline section (chronological):**
- Creation event (grey dot)
- Each status history entry (coloured dot by status)
- Each comment (chat bubble style)
- Resolution event (green dot)
- Feedback stars (if given)

**Side panel (Secretary only):**
- Assign staff dropdown
- Current assignee name and trade

**Action bar:**
- Status update dropdown + remark (staff / secretary)
- Reopen button (resident, within 7 days of resolution)
- Feedback form (resident, after resolution)

---

### Output 5 — Dues List (`/dues/`)

**Filters (top):** Month, Year, Status (Pending / Partial / Paid), Building

**Table columns:** Flat, Building, Resident, Month/Year, Amount Due, Amount Paid, Balance, Status badge, Actions

**Summary row (footer):** Total due, Total collected, Total pending

**Resident view:** Shows only their own flat's dues.

---

### Output 6 — Payment Receipt (`/dues/receipt/<payment_id>/`)

Printable A4 layout:

```
╔══════════════════════════════════════════╗
║          NivasSetu — Payment Receipt     ║
╠══════════════════════════════════════════╣
║ Receipt No : RCP-20261101-0001           ║
║ Date       : 01 November 2026            ║
╠══════════════════════════════════════════╣
║ Flat       : Wing A — A-101              ║
║ Resident   : Amit Sharma                 ║
║ Period     : November 2026               ║
╠══════════════════════════════════════════╣
║ Total Due  : ₹ 3,500.00                  ║
║ Amount Paid: ₹ 3,500.00                  ║
║ Mode       : UPI                         ║
║ Reference  : UPI123456789                ║
╠══════════════════════════════════════════╣
║ Status     : PAID  ✓                     ║
╚══════════════════════════════════════════╝
```

A "Print" button triggers `window.print()`.

---

### Output 7 — Reports Overview (`/reports/`)

| Section | Chart Type | Data |
|---------|-----------|------|
| Ticket Status | Doughnut (Chart.js) | Count per status |
| Resolution Time | Stat card | Average hours (resolved tickets only) |
| Top Categories | Horizontal bar | Top 5 categories by ticket count |
| Dues Summary | Stat cards | Total generated, Total collected, Total pending |

Export buttons: **Download Complaints CSV**, **Download Dues CSV**

---

### Output 8 — Audit Trail (`/audit/`)

**Table columns:** Timestamp, Actor (username), Action, Target, Before, After

**Features:** Paginated (20 per page), filtered by date range, immutable (no delete/edit in UI).

---

## 5.4 Validation Summary

| Rule | Applied to | Error shown |
|------|-----------|-------------|
| Minimum length | Description (20 chars), Comment (1 char) | Below field, red text |
| Maximum length | Description (2000), Remark (500), Reference (100) | Below field, red text |
| File type | Photo upload (JPEG/PNG only) | Below field |
| File size | Photo ≤ 5 MB | Below field |
| Future date only | Notice expiry | Below field |
| Payment ≤ outstanding | Payment amount | Below field, shows balance |
| Unique period | Dues generation month+year | Form-level error |
| Rating range | Feedback rating 1–5 | Radio buttons enforce this |
| CSRF | All POST forms | 403 page on mismatch |

---

## 5.5 Status Badge Colors

| Status | Tailwind classes (light) | Tailwind classes (dark) |
|--------|--------------------------|------------------------|
| OPEN | bg-blue-100 text-blue-800 | dark:bg-blue-900/40 dark:text-blue-300 |
| ASSIGNED | bg-purple-100 text-purple-800 | dark:bg-purple-900/40 |
| IN_PROGRESS | bg-yellow-100 text-yellow-800 | dark:bg-yellow-900/40 |
| RESOLVED | bg-green-100 text-green-800 | dark:bg-green-900/40 |
| CLOSED | bg-gray-100 text-gray-700 | dark:bg-gray-700 |
| OVERDUE | bg-red-100 text-red-800 | dark:bg-red-900/40 |

| Priority | Tailwind classes |
|----------|-----------------|
| LOW | bg-slate-100 text-slate-700 |
| MEDIUM | bg-amber-100 text-amber-800 |
| HIGH | bg-orange-100 text-orange-800 |
| CRITICAL | bg-red-100 text-red-800 font-bold |

