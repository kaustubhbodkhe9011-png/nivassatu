# Chapter 2 — Software Requirements Specification (SRS)

**Project:** NivasSetu — Housing Society Complaint & Dues Management Portal  
**Version:** 1.0  **Date:** November 2026  **Standard:** IEEE 830-1998 (adapted)

---

## 2.1 Introduction

### 2.1.1 Purpose
This document specifies the functional and non-functional requirements of **NivasSetu**, a web-based portal that allows housing-society residents to raise maintenance complaints online, enables secretaries to assign staff and track SLA deadlines, and manages monthly maintenance dues with an auditable payment record.

### 2.1.2 Scope
NivasSetu is a single-site Django application deployed on a local or cloud server. It covers:

- Role-based login and dashboards
- Building / flat / resident master data
- Full complaint lifecycle management
- Notice publishing with read-receipts
- Maintenance dues generation and manual payment recording
- Analytics reports and CSV exports
- Audit trail of every significant action

Out of scope (Phase 2, not yet implemented):
- SMS / e-mail push notifications
- Online payment gateway integration
- Mobile native app
- English–Marathi language toggle

### 2.1.3 Definitions

| Term | Meaning |
|------|---------|
| Secretary | Society administrator who manages all data |
| Resident | Flat owner or tenant who raises complaints |
| Staff | Maintenance technician assigned to complaints |
| Ticket | A single complaint record |
| SLA | Service-Level Agreement deadline (hours from creation) |
| Dues | Monthly maintenance charge per flat |

---

## 2.2 Overall Description

### 2.2.1 Product Perspective
NivasSetu replaces paper registers and WhatsApp threads with a structured web portal accessible from any browser on a smartphone or desktop.

```
┌────────────┐  HTTPS  ┌─────────────────┐  ORM  ┌──────────┐
│  Browser   │◄───────►│  Django Server  │◄─────►│ SQLite / │
│(any device)│         │  (Views + HTMX) │       │ PostgreSQL│
└────────────┘         └─────────────────┘       └──────────┘
```

### 2.2.2 User Classes

| Role | Access Level | Primary Activities |
|------|--------------|--------------------|
| **Secretary** | Full admin | Manage all entities, assign staff, generate dues, view reports |
| **Resident** | Own data only | Raise complaints, view notices, pay dues, give feedback |
| **Staff** | Assigned tickets only | View assigned complaints, update status with remarks |

### 2.2.3 Assumptions
- One society per deployment (single-tenant)
- Internet browser with JavaScript enabled
- Secretary manually enters payment references (no payment gateway)
- Photo uploads stored on local disk (configure MEDIA_ROOT in production)

---

## 2.3 Functional Requirements

### FR-01 — Accounts Module
| ID | Requirement |
|----|-------------|
| FR-01-1 | The system shall allow any registered user to log in with username and password. |
| FR-01-2 | On successful login, the system shall redirect the user to a role-specific dashboard. |
| FR-01-3 | Unauthenticated access to any protected URL shall redirect to the login page. |
| FR-01-4 | A logged-in user shall be able to change their password. |
| FR-01-5 | The system shall support three roles: SECRETARY, RESIDENT, STAFF. |
| FR-01-6 | Only a Secretary can create or deactivate user accounts via Django Admin. |

### FR-02 — Society Setup Module
| ID | Requirement |
|----|-------------|
| FR-02-1 | The Secretary shall be able to add Buildings (wings) with a name and description. |
| FR-02-2 | The Secretary shall be able to add Flats to a building, specifying flat number, floor, type and area. |
| FR-02-3 | The Secretary shall be able to assign a registered Resident user to a flat. |
| FR-02-4 | The system shall distinguish Owner and Tenant occupancy types. |
| FR-02-5 | Staff members shall have a profile that records their trade and contact number. |

### FR-03 — Complaints Module
| ID | Requirement |
|----|-------------|
| FR-03-1 | A Resident shall be able to create a complaint by selecting a category, entering a description, choosing a priority (Low / Medium / High / Critical), and optionally attaching a photo. |
| FR-03-2 | The system shall auto-generate a unique ticket number (NS-YYYYMMDD-NNNN). |
| FR-03-3 | The system shall auto-calculate an SLA deadline based on priority: Critical=4 h, High=24 h, Medium=72 h, Low=168 h. |
| FR-03-4 | The complaint status shall follow: Open → Assigned → In Progress → Resolved → Closed. |
| FR-03-5 | A Resident shall be able to Reopen a resolved complaint within 7 days of resolution. |
| FR-03-6 | The system shall mark a ticket as Overdue if the current time exceeds the SLA deadline and status is not Resolved or Closed. |
| FR-03-7 | A Secretary shall be able to assign a complaint to a Staff member. |
| FR-03-8 | A Staff member shall be able to update status and add remarks. |
| FR-03-9 | Any stakeholder may add a comment to a complaint thread. |
| FR-03-10 | The system shall record every status change in a history table with timestamp and actor. |
| FR-03-11 | A Resident shall be able to give a star rating (1–5) and text feedback after resolution. |

### FR-04 — Notices Module
| ID | Requirement |
|----|-------------|
| FR-04-1 | A Secretary shall be able to create a notice with title, body, category and optional expiry date. |
| FR-04-2 | A Secretary shall be able to pin important notices. |
| FR-04-3 | A Resident shall be able to acknowledge (mark as read) any notice. |
| FR-04-4 | The Secretary dashboard shall show how many residents have acknowledged each notice. |

### FR-05 — Dues and Payments Module
| ID | Requirement |
|----|-------------|
| FR-05-1 | The Secretary shall be able to define a MaintenancePlan with a base charge and a per-sq-ft rate. |
| FR-05-2 | The Secretary shall be able to generate DuesRecords for all flats for a chosen month/year. |
| FR-05-3 | The calculated due = base_charge + rate_per_sqft × flat_area, rounded to 2 decimal places. |
| FR-05-4 | The Secretary shall be able to record a manual payment against a DuesRecord, specifying mode (Cash / UPI / Cheque) and an optional reference number. |
| FR-05-5 | The system shall auto-generate a unique receipt number (RCP-YYYYMMDD-NNNN). |
| FR-05-6 | A Resident shall be able to view their own dues and payment history. |
| FR-05-7 | The system shall display a printable receipt page. |

### FR-06 — Reports Module
| ID | Requirement |
|----|-------------|
| FR-06-1 | The Secretary dashboard shall display: total open tickets, overdue count, resolved this month, dues pending total. |
| FR-06-2 | The reports page shall display a doughnut chart of ticket distribution by status. |
| FR-06-3 | The reports page shall display average resolution time in hours. |
| FR-06-4 | The reports page shall display top-5 complaint categories by frequency. |
| FR-06-5 | The Secretary shall be able to export all complaints to CSV. |
| FR-06-6 | The Secretary shall be able to export all dues to CSV. |

### FR-07 — Audit Log
| ID | Requirement |
|----|-------------|
| FR-07-1 | The system shall record an audit entry whenever a complaint status changes, a payment is recorded, or a notice is created. |
| FR-07-2 | Each audit entry shall store: actor, action verb, target object description, timestamp, and before/after values. |
| FR-07-3 | Only the Secretary can view the audit trail page. |

### FR-08 — Search and Filters
| ID | Requirement |
|----|-------------|
| FR-08-1 | The complaint list shall be filterable by status, category, priority, and building without a full page reload (HTMX). |
| FR-08-2 | HTMX partial responses shall update only the ticket table, not the whole page. |

---

## 2.4 Non-Functional Requirements

### NFR-01 — Performance
- Pages must load within 3 seconds on a local network.
- Complaint list with 1000 rows must respond within 2 seconds (database indexes on status, priority, created_at).

### NFR-02 — Security
- All passwords are stored as Django PBKDF2 hashes (never plain text).
- Each view is protected by a `@login_required` decorator and a role check.
- File uploads are saved to a server-only directory (not served from code root).
- CSRF tokens are included on all POST forms.
- DEBUG is set to False in production settings.

### NFR-03 — Usability / Accessibility
- Mobile-first responsive layout; bottom navigation bar on screens < 768 px.
- All form inputs have visible `<label>` elements.
- Focus states styled for keyboard navigation.
- Color contrast ratio ≥ 4.5:1 (WCAG AA) for all text.
- Dark mode available via a toggle stored in `localStorage`.
- Empty states display a helpful message and an action button.

### NFR-04 — Maintainability
- Code organised into separate Django apps (one per domain).
- Each function and class has a one-line docstring.
- `ruff` linter enforced; no unused imports.
- Settings split into `base.py`, `dev.py`, `prod.py` via environment variable.

### NFR-05 — Portability
- Switching from SQLite to PostgreSQL requires only changing the `DATABASE_URL` environment variable.
- All static files can be collected with `python manage.py collectstatic` for deployment.

### NFR-06 — Reliability
- Atomic database transactions used for dues generation and payment recording to prevent partial writes.
- 14 automated pytest tests cover the core logic of every module.

---

## 2.5 Hardware Requirements

| Component | Minimum Specification |
|-----------|-----------------------|
| Server CPU | Dual-core 1.5 GHz |
| Server RAM | 2 GB |
| Disk space | 2 GB (10 GB if photo uploads are heavy) |
| Client device | Any smartphone or PC with a modern browser |
| Network | Local LAN or internet connection |

---

## 2.6 Software Requirements

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11+ | Runtime |
| Django | 6.1 | Web framework |
| SQLite | 3.x (bundled) | Development database |
| PostgreSQL | 14+ | Production database |
| pytest + pytest-django | 9.x + 4.x | Automated testing |
| ruff | 0.17+ | Linting |
| Pillow | 10+ | Photo upload processing |
| python-decouple | 3.x | .env configuration |
| Tailwind CSS CDN | Play CDN | Utility CSS framework |
| HTMX | 2.x CDN | Partial page updates |
| Chart.js | 4.x CDN | Dashboard charts |
| Lucide Icons | CDN | SVG icon set |
| Inter font | Google Fonts CDN | Typography |

---

## 2.7 Input / Output Requirements

### Inputs
| Input | Form | Key Fields |
|-------|------|-----------|
| Login credentials | /accounts/login/ | username, password |
| New complaint | /complaints/create/ | category, description, priority, photo |
| Status update | Complaint detail | new_status, remark |
| New notice | /notices/create/ | title, body, category, is_pinned, expires_on |
| Payment record | /dues/pay/<id>/ | amount, mode, reference, paid_on |
| Dues generation | /dues/generate/ | plan, month, year |
| Staff assignment | Complaint detail | staff_member |
| Feedback | Complaint detail | rating (1–5), text |

### Outputs
| Output | URL | Description |
|--------|-----|-------------|
| Secretary dashboard | /dashboard/ | Summary cards + pending list |
| Complaint detail | /complaints/<id>/ | Timeline, comments, assignment panel |
| Dues list | /dues/ | Table with status badges, pending total |
| Payment receipt | /dues/receipt/<id>/ | Printable A4 receipt |
| Reports page | /reports/ | Charts + summary statistics |
| Audit trail | /audit/ | Tabular log with actor and timestamp |
| Complaints CSV | /reports/export/complaints/ | Download as .csv |
| Dues CSV | /reports/export/dues/ | Download as .csv |

---

## 2.8 Constraints

1. Single-tenant: one society per server instance.
2. Photo uploads stored locally; no CDN or object-storage integration in Phase 1.
3. Payments recorded manually by Secretary; no payment-gateway API.
4. All text content is in English only (Marathi i18n is Phase 2).
5. Demo seed data must be clearly labelled and must not resemble real personal data.

---

## 2.9 Assumptions

1. The Secretary creates all resident and staff user accounts before first use.
2. Building names and flat numbers will not change after dues records are generated.
3. The server clock is set to IST (Asia/Kolkata); SLA deadlines are calculated in this timezone.
4. At least one complaint category must exist before residents can file a complaint.
5. The society runs one MaintenancePlan at a time per period.

