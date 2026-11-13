# Viva Notes — NivasSetu

**Project:** NivasSetu  **Exam:** S.Y.B.Sc. CS Semester III Mini Project Viva  
**Student tip:** Read each section aloud once. For the "Explain in simple words" boxes, speak from them directly.

---

## Part A — Module-by-Module Simple Explanations

### 1. Accounts Module
**What it does:** Handles login, logout, and decides which dashboard a user sees after logging in.

**Key file:** `apps/accounts/models.py`

We extended Django's built-in `AbstractUser` to add two extra fields: `role` (is this person a Secretary, Resident, or Staff?) and `phone_number`. When a user logs in, the `dashboard_view` in `apps/core/views.py` checks their role and redirects them to the right page.

> **Say this in viva:** "We used Django's AbstractUser so we didn't have to write authentication code from scratch. We just added a `role` field on top of it."

---

### 2. Society Module
**What it does:** Stores the building structure of the housing society — which wings exist, which flats are in each wing, and who lives in each flat.

**Tables:** `Building` → `Flat` → `ResidentProfile`

A `Building` is like Wing A or Wing B. A `Flat` belongs to one building (flat number, floor, type, area). A `ResidentProfile` links a User to a Flat and says whether they own it or rent it.

> **Say this in viva:** "The society module is the master data layer. Everything else — complaints, dues — is linked back to a Flat, which is linked to a Building."

---

### 3. Complaints Module
**What it does:** The heart of the system. Residents raise complaints; the secretary assigns them to staff; staff resolves them.

**Key concepts:**
- **Ticket number:** auto-generated as `NS-YYYYMMDD-NNNN` in `Complaint.save()`
- **SLA deadline:** auto-calculated based on priority: Critical=4h, High=24h, Medium=72h, Low=168h
- **`is_overdue` property:** returns True if the deadline has passed and status is not Resolved/Closed
- **`can_reopen` property:** returns True if status is Resolved and fewer than 7 days have passed since resolution
- **Status history:** every status change auto-creates a `ComplaintStatusHistory` row in `Complaint.save()`

> **Say this in viva:** "The status workflow goes Open → Assigned → In Progress → Resolved → Closed. I stored every transition in a history table so there is a full audit trail of who changed what and when."

---

### 4. Notices Module
**What it does:** Secretary posts notices (water cut, society meeting, etc.). Residents can acknowledge (mark as read). The secretary can see how many residents have read each notice.

**Key table:** `NoticeAcknowledgement` has a `UNIQUE(notice_id, resident_id)` constraint — so a resident can only mark a notice once.

> **Say this in viva:** "The acknowledgement table uses a unique constraint on the notice-resident pair so no duplicate acknowledgements are created."

---

### 5. Dues & Payments Module
**What it does:** Secretary creates a maintenance plan with a formula. The system calculates each flat's due = base charge + (rate × area). Secretary records cash/UPI/cheque payments manually.

**Formula in code:**
```python
amount = plan.base_charge + plan.rate_per_sqft * Decimal(str(flat.square_feet))
```
We used `Decimal(str(...))` because SQLite returns `float` but we need `Decimal` for precise money arithmetic.

**Receipt number:** auto-generated as `RCP-YYYYMMDD-NNNN` in `Payment.save()`

> **Say this in viva:** "We used Python's Decimal type for all money calculations to avoid floating-point rounding errors. For example, 0.1 + 0.2 in float gives 0.30000000000000004, but Decimal gives exactly 0.30."

---

### 6. Reports Module
**What it does:** Shows the secretary a summary of the society's health — how many complaints are open, how long they take to resolve, which category recurs most, and how much maintenance money has been collected.

**Charts used:** Chart.js doughnut chart (status distribution). Data is prepared server-side and passed to the template as JSON in a `<script>` tag.

> **Say this in viva:** "We calculate the chart data in Python using Django's ORM `.values().annotate(Count())` and pass it as JSON to Chart.js in the template."

---

### 7. Audit Log
**What it does:** Records who did what and when — complaint status changes, payment recording, notice creation. The log is immutable (no edit/delete in the UI). Only the secretary can see it.

**Helper function:** `audit/utils.py::record_audit(actor, action, target_description, before, after)` — called in views after a successful database change.

> **Say this in viva:** "The audit log is for accountability. If a complaint is wrongly closed or a payment is disputed, the secretary can open the audit trail and see exactly who made the change and at what time."

---

### 8. Seed Demo Command
**What it does:** Populates the database with realistic-looking fake data so the evaluator can explore the system without manual data entry.

**Run:**
```bash
python manage.py seed_demo
```

Creates: 1 society, 2 buildings (Wing A, Wing B), 30 flats (A-101 … A-115, B-101 … B-115), 10 resident users, 3 staff users, 40 complaints, 3 notices, dues records for all flats, payments for ~70% of flats.

**All data is fictional** — names like "Amit Demo", phones like 9000000001.

---

## Part B — 30 Viva Questions and Answers

### Django & Python

**Q1. What is Django and why did you use it?**  
Django is a Python web framework that follows the MTV (Model-Template-View) pattern. I used it because it has a built-in ORM, authentication system, admin panel, and form validation — which reduced the amount of code I had to write from scratch.

**Q2. What is the difference between Django's Model, View, and Template?**  
Model = Python class that maps to a database table. View = Python function that receives a request and returns a response. Template = HTML file with Jinja-like tags to display data passed by the view.

**Q3. What is `AbstractUser` and why did you extend it instead of creating a new User model?**  
`AbstractUser` is Django's built-in user model with login, password hashing, session handling already coded. By extending it (not replacing it), we keep all Django auth features and just add extra fields like `role` and `phone_number`.

**Q4. What does `@login_required` do?**  
It's a Python decorator that checks if the request user is authenticated. If not, it redirects to the login page (configured by `LOGIN_URL` in settings).

**Q5. What is Django's ORM?**  
ORM = Object-Relational Mapper. It lets us write Python code like `Complaint.objects.filter(status="OPEN")` instead of raw SQL. Django translates it to `SELECT * FROM complaints_complaint WHERE status = 'OPEN'`.

**Q6. What is a migration in Django?**  
A migration is a Python file that describes a change to the database schema (e.g., add a table, add a column). We run `python manage.py makemigrations` to generate it and `python manage.py migrate` to apply it.

**Q7. What is the difference between `null=True` and `blank=True` in Django models?**  
`null=True` allows NULL in the database column. `blank=True` allows an empty value in Django forms. For text fields, we usually use `blank=True` only (not null); for ForeignKey and date fields, we use `null=True, blank=True`.

**Q8. What is CSRF and how does Django handle it?**  
CSRF = Cross-Site Request Forgery. An attacker tricks a logged-in user into submitting a form on another site. Django prevents this by embedding a unique token in every form (`{% csrf_token %}`). The server checks this token on every POST request.

**Q9. What is HTMX and why did you use it instead of a JavaScript framework like React?**  
HTMX is a library that lets HTML attributes trigger AJAX requests and swap parts of the page. We used it for filtering the complaint list without a full page reload. We chose it over React because: (a) the stack requirement said no React, and (b) HTMX needs far less JavaScript for simple interactions.

**Q10. What is `python-decouple` and why is it important?**  
`python-decouple` reads settings from a `.env` file. This keeps secrets (database password, Django SECRET_KEY) out of the source code. We ship `.env.example` with safe placeholder values so the developer knows what to fill in.

---

### Database & 3NF

**Q11. What is 3NF and how is your database in 3NF?**  
3NF = Third Normal Form. Requirements:
1. 1NF: atomic values, no repeating groups ✓ (each cell has one value)
2. 2NF: no partial dependencies (every non-key field depends on the full primary key) ✓ (we separated plan-level data into `MaintenancePlan`, flat-level data into `Flat`)
3. 3NF: no transitive dependencies (non-key → non-key) ✓ (building name is in `Building` table, not repeated in `Flat`)

**Q12. What is a foreign key?**  
A foreign key is a field in one table that references the primary key of another table. For example, `Complaint.flat_id` references `Flat.id`. It enforces referential integrity — you cannot have a complaint pointing to a flat that doesn't exist.

**Q13. Why did you use `UNIQUE(month, year)` on `MaintenancePlan`?**  
To prevent accidentally generating duplicate dues for the same month. If you try to create two plans for November 2026, the database will raise an IntegrityError.

**Q14. What is the difference between `OneToOneField` and `ForeignKey`?**  
`ForeignKey` = many-to-one (many complaints can belong to one flat). `OneToOneField` = one-to-one (each user has exactly one ResidentProfile). Internally, `OneToOneField` is a `ForeignKey` with `unique=True`.

**Q15. What is an index and when did you use them?**  
An index speeds up `WHERE` clause lookups. Django automatically creates an index on ForeignKey fields and fields with `unique=True`. We added `db_index=True` on `Complaint.status`, `Complaint.priority`, and `Complaint.created_at` because these are frequently filtered.

---

### Application Logic

**Q16. How does the ticket number get generated?**  
In `Complaint.save()`, before calling `super().save()`, we check if `ticket_number` is blank. If so, we build it as:
```python
date_str = now().strftime("%Y%m%d")
count = Complaint.objects.filter(ticket_number__startswith=f"NS-{date_str}").count() + 1
self.ticket_number = f"NS-{date_str}-{count:04d}"
```

**Q17. How is the SLA deadline calculated?**  
In `Complaint.save()`:
```python
SLA_HOURS = {"LOW": 168, "MEDIUM": 72, "HIGH": 24, "CRITICAL": 4}
hours = SLA_HOURS.get(self.priority, 72)
self.sla_deadline = now() + timedelta(hours=hours)
```
So a Critical ticket has a 4-hour deadline from creation.

**Q18. How does the `is_overdue` property work?**  
```python
@property
def is_overdue(self):
    if self.status in ("RESOLVED", "CLOSED"):
        return False
    return now() > self.sla_deadline
```
It's a Python property (not a database column), computed on demand.

**Q19. How does the resident reopen a complaint?**  
`can_reopen` property checks:
```python
@property
def can_reopen(self):
    if self.status != "RESOLVED":
        return False
    resolved_entry = self.statushistory.filter(new_status="RESOLVED").last()
    if not resolved_entry:
        return False
    return (now() - resolved_entry.changed_at).days <= 7
```
If True, a "Reopen" button appears on the complaint detail page.

**Q20. How does the dues calculation work?**  
```python
def calculate_due_for_flat(self, flat):
    return self.base_charge + self.rate_per_sqft * Decimal(str(flat.square_feet))
```
For example: base=₹2000, rate=₹1.50/sq ft, area=1000 sq ft → ₹2000 + ₹1500 = ₹3500.

**Q21. Why did you wrap `flat.square_feet` in `Decimal(str(...))`?**  
SQLite returns `DecimalField` values as Python `float` in some Django versions. Multiplying `float * Decimal` raises `TypeError`. Wrapping with `Decimal(str(value))` converts it safely.

**Q22. What is role-based access control and how is it implemented?**  
Different users can see different pages. We implemented this with custom decorators in `apps/accounts/decorators.py`:
```python
def secretary_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_secretary:
            return HttpResponseForbidden()
        return view_func(request, *args, **kwargs)
    return wrapper
```
Applied as `@secretary_required` on views that only the secretary should access.

**Q23. How does the HTMX complaint filter work?**  
The filter form has `hx-get="/complaints/"` and `hx-target="#ticket-table"`. When a dropdown changes, HTMX sends a GET request with query params to `/complaints/`. The view detects `HX-Request` header and returns only the `partials/ticket_table.html` fragment, not the full page. HTMX swaps the `#ticket-table` div with this fragment.

**Q24. How did you implement the audit log?**  
`apps/audit/utils.py` has a helper:
```python
def record_audit(actor, action, target_description, before=None, after=None):
    AuditLog.objects.create(
        actor=actor,
        action=action,
        target_description=target_description,
        before_value=before,
        after_value=after,
    )
```
Called in views after each significant DB change, e.g., after updating complaint status.

**Q25. How does dark mode work?**  
The `<html>` tag gets a `dark` class when dark mode is active (Tailwind's `darkMode: 'class'` strategy). A small `<script>` tag in `base.html` reads `localStorage.getItem('darkMode')` on page load and toggles the class. A button click toggles the class and saves to localStorage so the preference persists across pages.

---

### Design & Architecture

**Q26. What is the 3-tier architecture of your application?**  
1. **Presentation tier:** Browser — renders HTML from Django templates, Tailwind CSS, Chart.js
2. **Application tier:** Django server — URL routing, views (business logic), forms (validation), ORM queries
3. **Data tier:** SQLite (dev) or PostgreSQL (prod) database

**Q27. What is a DFD and what levels did you create?**  
DFD = Data Flow Diagram. It shows how data moves through a system.
- Level 0 (Context diagram): system as one black box, all external actors around it
- Level 1: system split into major processes (Auth, Complaints, Dues, Notices, Reports, Audit)
- Level 2: Complaint process expanded — create, validate, assign, update, comment, feedback

**Q28. What is the difference between a Use Case diagram and a Sequence diagram?**  
- Use Case diagram: shows WHAT actors can do (high-level, no order)
- Sequence diagram: shows HOW a specific interaction happens step-by-step in time (messages between browser, view, model, database)

**Q29. How would you deploy NivasSetu in production?**  
1. Set `DEBUG=False` in `.env`
2. Set a strong `SECRET_KEY`
3. Set `DATABASE_URL` to PostgreSQL connection string
4. Run `python manage.py collectstatic` to collect static files
5. Use gunicorn as the WSGI server: `gunicorn config.wsgi:application`
6. Deploy on Render or Railway (they auto-detect Python apps, run build command, start gunicorn)

**Q30. If you had to add email notifications, what would you change?**  
1. Add `EMAIL_BACKEND` settings in `base.py`
2. In `Complaint.save()` (or via Django signals in a `post_save` signal handler), send an email using `django.core.mail.send_mail()` when status changes
3. This keeps the email logic separate from the view logic (single responsibility)

---

## Part C — Hands-On Exercises

### Exercise 1 — Add a new complaint priority: EMERGENCY
**Files to change:**
1. `apps/complaints/models.py` — add `EMERGENCY = "EMERGENCY", "Emergency"` to `Priority` class
2. `apps/complaints/models.py` — add `"EMERGENCY": 1` to `SLA_HOURS` dict (1 hour)
3. `apps/complaints/forms.py` — no change needed (auto-picks up from model)
4. Run `python manage.py makemigrations complaints` and `python manage.py migrate`
5. Update the status badge color in `base.html` or the template

---

### Exercise 2 — Add a due date to DuesRecord (penalty after due date)
**Files to change:**
1. `apps/dues/models.py` — add `due_date = models.DateField(null=True, blank=True)` to `DuesRecord`
2. `apps/dues/views.py` — in `generate_dues`, compute `due_date = last day of that month`
3. `apps/dues/models.py` — add `is_overdue` property: `return date.today() > self.due_date if self.due_date else False`
4. Run `makemigrations` and `migrate`
5. Update `dues_list.html` to show an overdue badge

---

### Exercise 3 — Allow residents to upload a photo when creating a complaint
**Files to check:** Already implemented.
- `Complaint.photo = models.ImageField(upload_to="complaints/", null=True, blank=True)`
- `ComplaintForm` includes `photo` field with `enctype="multipart/form-data"` on the form tag
- `create_complaint` view: `form = ComplaintForm(request.POST, request.FILES)`
- `MEDIA_ROOT` and `MEDIA_URL` configured in `settings/base.py`

---

### Exercise 4 — Add a simple search box to the complaint list
**Files to change:**
1. `apps/complaints/views.py` — in `complaint_list`, read `q = request.GET.get("q", "")` and add:
   ```python
   if q:
       qs = qs.filter(description__icontains=q) | qs.filter(ticket_number__icontains=q)
   ```
2. `templates/complaints/complaint_list.html` — add a text input with `name="q"` inside the HTMX filter form
3. The HTMX setup already handles this — `hx-get` sends all form fields including `q`

---

### Exercise 5 — Change SLA for Medium priority from 72 hours to 48 hours
**File:** `apps/complaints/models.py`
```python
SLA_HOURS = {
    "LOW": 168,
    "MEDIUM": 48,   # changed from 72
    "HIGH": 24,
    "CRITICAL": 4,
}
```
No migration needed (SLA_HOURS is application logic, not stored in the DB; existing tickets keep their old deadlines, new ones get 48 hours).

**Update the test:** `tests/test_complaints.py::test_complaint_sla` — change the assertion for MEDIUM from `72` to `48`.

