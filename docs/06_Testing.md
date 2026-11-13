# Chapter 6 — Implementation & Testing

**Project:** NivasSetu  **Version:** 1.0

---

## 6.1 Implementation Overview

### Technology Summary

| Technology | Version | Role |
|-----------|---------|------|
| Python | 3.14.0 | Backend runtime |
| Django | 6.1.3 | Web framework (MVC pattern) |
| SQLite | bundled | Development database |
| HTMX | 2.x CDN | Partial page updates (no JS framework) |
| Tailwind CSS | Play CDN | Utility-first styling |
| Chart.js | 4.x CDN | Dashboard bar/doughnut charts |
| Lucide Icons | CDN | SVG icon set |
| Inter | Google Fonts CDN | Typography |
| pytest | 9.2.0 | Test runner |
| pytest-django | 4.14.0 | Django test fixtures |
| Pillow | 13.0.0 | Photo upload processing |
| python-decouple | 3.8 | .env configuration |
| ruff | 0.17.4 | Linter |

---

### 6.1.1 App: `apps/accounts`

**Purpose:** Authentication, user model, role-based access control.

| File | Description |
|------|-------------|
| `models.py` | Custom `User` model extending `AbstractUser`; adds `role` (SECRETARY/RESIDENT/STAFF) and `phone_number` fields; helper properties `is_secretary`, `is_resident`, `is_staff_member` |
| `views.py` | `LoginView` (custom form + demo-credential auto-fill), `LogoutView`, `ProfileView`, `ChangePasswordView` |
| `forms.py` | `LoginForm` (username + password), `UserProfileForm` |
| `decorators.py` | `role_required`, `secretary_required`, `resident_required`, `staff_required` — wrap Django's `@login_required` |
| `urls.py` | Routes: `/accounts/login/`, `/accounts/logout/`, `/accounts/profile/`, `/accounts/password/` |
| `admin.py` | `UserAdmin` registered; secretary creates users through Django Admin |
| `apps.py` | `AccountsConfig` with `default_auto_field = "django.db.models.BigAutoField"` |

---

### 6.1.2 App: `apps/core`

**Purpose:** Landing page, dashboard dispatcher, seed_demo command.

| File | Description |
|------|-------------|
| `views.py` | `landing_view` (public), `dashboard_view` (dispatches to role-specific sub-view), `secretary_dashboard`, `resident_dashboard`, `staff_dashboard` |
| `context_processors.py` | Injects `society` object into all templates |
| `management/commands/seed_demo.py` | Creates all demo data: 1 society, 2 buildings, 30 flats, 10 residents, 3 staff, 40 complaints, 3 notices, dues, payments, audit logs |

---

### 6.1.3 App: `apps/society`

**Purpose:** Building, Flat, ResidentProfile, StaffProfile master data.

| File | Description |
|------|-------------|
| `models.py` | `Society`, `Building`, `Flat` (with `FlatType` choices), `ResidentProfile` (with `OccupancyType`), `StaffProfile` |
| `views.py` | `flat_list`, `add_flat`, `resident_list`, `assign_resident` — all secretary-only |
| `forms.py` | `FlatForm`, `AssignResidentForm` |
| `urls.py` | Routes under `/society/` |

---

### 6.1.4 App: `apps/complaints`

**Purpose:** Full complaint lifecycle management.

| File | Description |
|------|-------------|
| `models.py` | `ComplaintCategory`, `Complaint` (auto ticket number, SLA deadline, `is_overdue` property, `can_reopen` property), `ComplaintStatusHistory` (auto-created on `save()`), `ComplaintComment`, `ComplaintFeedback` |
| `views.py` | `complaint_list` (HTMX filtered), `create_complaint`, `complaint_detail`, `assign_staff`, `update_status`, `add_comment`, `submit_feedback` |
| `forms.py` | `ComplaintForm`, `AssignStaffForm`, `UpdateStatusForm`, `CommentForm`, `FeedbackForm` |
| `urls.py` | Routes under `/complaints/` |
| `templates/complaints/partials/ticket_table.html` | HTMX target — only the table is replaced on filter |

**SLA hours by priority:**
```python
SLA_HOURS = {"LOW": 168, "MEDIUM": 72, "HIGH": 24, "CRITICAL": 4}
```

---

### 6.1.5 App: `apps/notices`

**Purpose:** Notice publishing with read receipts.

| File | Description |
|------|-------------|
| `models.py` | `Notice` (with `NoticeCategory` choices, `is_pinned`, `expires_on`), `NoticeAcknowledgement` |
| `views.py` | `notice_list`, `create_notice` (secretary), `acknowledge_notice` (resident, HTMX) |
| `forms.py` | `NoticeForm` |
| `urls.py` | Routes under `/notices/` |

---

### 6.1.6 App: `apps/dues`

**Purpose:** Maintenance dues generation and manual payment recording.

| File | Description |
|------|-------------|
| `models.py` | `MaintenancePlan` (base + per-sq-ft formula, `calculate_due_for_flat()`), `DuesRecord` (PENDING/PARTIAL/PAID status), `Payment` (auto receipt number) |
| `views.py` | `dues_list`, `generate_dues` (creates one DuesRecord per flat), `record_payment`, `receipt` |
| `forms.py` | `GenerateDuesForm`, `PaymentForm` |
| `urls.py` | Routes under `/dues/` |

**Key fix:** `calculate_due_for_flat()` wraps `flat.square_feet` in `Decimal(str(...))` to avoid SQLite returning a Python `float` that cannot be multiplied with `Decimal`.

---

### 6.1.7 App: `apps/reports`

**Purpose:** Dashboard analytics and CSV exports.

| File | Description |
|------|-------------|
| `views.py` | `reports_overview_view` (chart data via Django ORM aggregations), `export_complaints_csv`, `export_dues_csv` |
| `urls.py` | Routes under `/reports/` |
| `templates/reports/overview.html` | Chart.js doughnut for status distribution; stat cards for avg resolution time and top categories |

---

### 6.1.8 App: `apps/audit`

**Purpose:** Immutable audit trail of significant actions.

| File | Description |
|------|-------------|
| `models.py` | `AuditLog` model with actor, action, target_description, before_value, after_value, timestamp |
| `utils.py` | `record_audit(actor, action, target_description, before=None, after=None)` — called by complaints and dues views |
| `views.py` | `audit_trail_view` — paginated, secretary-only |
| `urls.py` | Route `/audit/` |

---

## 6.2 Test Environment

```
platform win32
Python  : 3.14.0
pytest  : 9.2.0
pytest-django : 4.14.0
Django  : 6.1.3
Database: SQLite (in-memory test DB, isolated per test session)
```

**Run command:**
```bash
.\venv\Scripts\pytest --tb=short -q
```

---

## 6.3 Test Case Table

| TC-ID | Test Function | Module | Input / Setup | Expected Result | Actual Result | Status |
|-------|--------------|--------|--------------|----------------|---------------|--------|
| TC-01 | `test_user_roles` | Accounts | Create User with each role | `is_secretary`, `is_resident`, `is_staff_member` return correctly | Returns True/False as expected | ✅ PASS |
| TC-02 | `test_login_redirect_by_role` | Accounts | POST login with secretary credentials | Redirect to `/dashboard/` | 302 → /dashboard/ | ✅ PASS |
| TC-03 | `test_unauthenticated_redirect` | Accounts | GET protected URL without login | Redirect to login page | 302 → /accounts/login/ | ✅ PASS |
| TC-04 | `test_flat_naming` | Society | Create Building + Flat | `str(flat)` returns "Wing A — A-101" | Returns correct string | ✅ PASS |
| TC-05 | `test_occupancy_types` | Society | Create OWNER and TENANT profiles | Both occupancy_type values stored correctly | Stored and retrieved correctly | ✅ PASS |
| TC-06 | `test_staff_profile` | Society | Create StaffProfile for staff user | Trade and phone stored; linked to User | Fields match; FK correct | ✅ PASS |
| TC-07 | `test_secretary_access_control` | Society | Resident GET `/society/flats/` | 302 redirect (access denied) | 302 as expected | ✅ PASS |
| TC-08 | `test_complaint_sla` | Complaints | Create complaints with CRITICAL and LOW priority | CRITICAL SLA ≈ 4 h; LOW SLA ≈ 168 h; is_overdue=False initially | SLA calculated correctly; overdue=False | ✅ PASS |
| TC-09 | `test_complaint_state_machine` | Complaints | Transition OPEN→ASSIGNED→IN_PROGRESS→RESOLVED; then reopen after 7 days | can_reopen=True within 7 days; can_reopen=False after | State machine behaves correctly | ✅ PASS |
| TC-10 | `test_resident_isolation` | Complaints | Resident A queries complaint list | Only own complaints returned | QuerySet contains only resident's own complaints | ✅ PASS |
| TC-11 | `test_notice_and_acknowledgement` | Notices | Create notice; resident acknowledges | Acknowledgement saved; count=1; second ack does not duplicate | Unique constraint enforced | ✅ PASS |
| TC-12 | `test_dues_and_payment` | Dues | Generate dues for flat (1000 sq ft, base=2000, rate=1.5); record full payment | amount_due=3500.00; status changes PENDING→PAID | Decimal calculation correct; status updated | ✅ PASS |
| TC-13 | `test_audit_logging` | Reports/Audit | Trigger complaint status change | AuditLog entry created with correct actor and action | Entry found in DB | ✅ PASS |
| TC-14 | `test_csv_exports` | Reports | Secretary GET `/reports/export/complaints/`; Resident GET same URL | Secretary: 200 + CSV content; Resident: 403 or redirect | Correct responses | ✅ PASS |

---

## 6.4 Real pytest Output

```
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.2.0, pluggy-1.7.0
django: version: 6.1.3, settings: config.settings.dev (from ini)
rootdir: C:\Users\acer\OneDrive\Desktop\NivasSetu
configfile: pytest.ini
plugins: django-4.14.0
collected 14 items

tests\test_accounts.py ...                                               [ 21%]
tests\test_complaints.py ...                                             [ 42%]
tests\test_dues.py .                                                     [ 50%]
tests\test_notices.py .                                                  [ 57%]
tests\test_reports.py ..                                                 [ 71%]
tests\test_society.py ....                                               [100%]

======================== 14 passed in 94.90s (0:01:34) ========================
```

**Result: 14/14 tests passed. 0 failures. 0 errors.**

---

## 6.5 Known Limitations of Current Tests

- Tests use an in-memory SQLite test database; they do not test PostgreSQL compatibility.
- Photo upload tests are not included (file I/O in CI is optional).
- HTMX partial-response behavior is tested only at the view level (HTTP status codes), not via browser automation.
- No load or performance tests have been written.

---

## 6.6 Screenshot Placeholders

> **[Student action required]** Take screenshots of the running application and insert them below:

| Screen | Caption |
|--------|---------|
| `screenshots/01_landing.png` | Landing page with demo login buttons |
| `screenshots/02_secretary_dashboard.png` | Secretary dashboard with summary cards |
| `screenshots/03_resident_dashboard.png` | Resident dashboard view |
| `screenshots/04_complaint_list.png` | Complaint list with HTMX filters |
| `screenshots/05_complaint_detail.png` | Complaint detail timeline with comments |
| `screenshots/06_create_complaint.png` | Complaint creation form |
| `screenshots/07_notice_list.png` | Notice list with Acknowledge button |
| `screenshots/08_dues_list.png` | Dues list with status badges |
| `screenshots/09_receipt.png` | Printable payment receipt |
| `screenshots/10_reports.png` | Reports page with Chart.js chart |
| `screenshots/11_audit_trail.png` | Audit trail page |
| `screenshots/12_pytest_output.png` | Terminal showing 14 passed |

