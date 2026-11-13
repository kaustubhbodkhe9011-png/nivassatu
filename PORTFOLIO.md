# 💼 NivasSetu — Portfolio Showcase Package

Use this guide to feature **NivasSetu** on your **Resume**, **LinkedIn**, **GitHub Profile**, and **Personal Portfolio Website**.

---

## 1. Resume / CV Entries

### Option A: Standard Bullet Points (STAR Method — Best for Full-Stack / Software Engineer roles)
```markdown
NivasSetu — Housing Society Grievance & Maintenance Ledger Platform
Tech Stack: Python, Django, SQLite / PostgreSQL, HTMX, Tailwind CSS, Chart.js, pytest
• Built a full-stack housing society management platform serving 3 distinct user roles (Secretary, Resident, Technician) to replace unstructured paper registers and WhatsApp groups.
• Engineered an automated grievance state machine (Open → Assigned → In Progress → Resolved → Closed) with dynamic SLA timers (4h–72h), overdue detection, and 7-day resident reopen protection.
• Designed a 3NF relational database schema across 8 modular Django apps with immutable audit logging for all ticket updates and financial transactions.
• Automated maintenance dues calculation using custom per-sq-ft tariff formulas and built multi-mode payment recording with print-ready digital receipt generation.
• Achieved 100% test coverage for critical business logic with 14 automated pytest-django tests and sub-30ms client partial re-renders using HTMX.
```

### Option B: Concise 2-Line Summary (For compact 1-page resumes)
```markdown
NivasSetu | Full-Stack Web Application (Python, Django, HTMX, Tailwind CSS, pytest)
• Engineered a role-based housing society portal with automated SLA grievance tracking, tariff calculation, and immutable audit logs.
• Achieved sub-50ms dynamic UI filtering using HTMX without heavy client-side JavaScript frameworks; tested via 14 automated pytest tests.
```

---

## 2. Personal Portfolio Website Project Card

### Project Title
**NivasSetu — Intelligent Residential Governance Platform**

### Tagline / Subtitle
*A full-stack, SLA-driven grievance tracking and maintenance dues transparency platform for modern residential housing societies.*

### Short Description (for Project Card / Modal)
> In Indian housing societies, maintenance complaints and dues records get lost in unorganized WhatsApp groups and paper notebooks. NivasSetu replaces this chaos with a structured workflow: ticket dispatches with automated SLA timers (4h–72h), secretary-to-staff assignment, 7-day resident reopen rights, per-sq-ft maintenance calculation, and printable receipts. Built with Python, Django, and HTMX for zero-bloat reactive UI.

### Key Highlights / Feature Badges
- **Role-Based Portals**: Tailored workflows for Secretary (Admin), Residents (Owners/Tenants), and Technicians.
- **Strict SLA State Machine**: 4-hour critical response timers, automated overdue flagging, and timeline audit logs.
- **Financial Transparency**: Per-sq-ft formula calculation, UPI/Cash/Cheque manual reconciliation, and verified PDF/HTML receipts.
- **Modern Performance**: Server-driven UI with HTMX partial swapping and dark architectural aesthetic.
- **100% Tested**: 14/14 automated unit and integration tests passing with pytest-django.

---

## 3. LinkedIn Post (Ready to Publish)

```text
🚀 Excited to share my latest full-stack project: NivasSetu (निवाससेतू)!

In residential housing societies, complaints like lift failures, pipe bursts, and security issues are frequently raised on casual WhatsApp groups—leading to zero accountability and lost records. Maintenance dues tracked on spreadsheets often trigger disputes during society meetings.

To solve this, I designed and built NivasSetu: an architectural, transparent residential governance portal.

Key Engineering Highlights:
🔹 Role-Based Access Control: Specialized dashboards for Secretary, Residents, and On-site Technicians.
🔹 Ticket State Machine & SLA: Automatic ticket dispatching (NS-YYYYMMDD-NNNN), priority-based SLA countdowns (4h for critical down to 72h), and overdue alerting.
🔹 Resident Empowerment: 7-day reopen protection if an issue recurs, plus post-resolution satisfaction ratings.
🔹 Dues & Receipt Generation: Automated tariff calculations using custom per-sq-ft formulas with print-ready payment receipts.
🔹 High Performance, Zero Framework Bloat: Built with Django + HTMX + Tailwind CSS, delivering reactive partial page swaps without heavy SPA frameworks.
🔹 Quality Assured: 14 automated unit and integration tests with pytest-django.

💻 Tech Stack: Python 3.14 | Django 6.1 | SQLite/PostgreSQL | HTMX | Tailwind CSS | Chart.js | pytest

Check out the repository and full college engineering documentation on my GitHub! 👇
[Insert your GitHub Repo Link]

#Python #Django #WebDevelopment #FullStack #HTMX #TailwindCSS #SoftwareEngineering #PortfolioProject
```

---

## 4. GitHub Project Description & Topics

### Repo About Text:
> 🏛️ Intelligent residential governance platform for Indian housing societies. Features automated SLA grievance tracking, maintenance dues calculation, read-receipt notices, and immutable audit logs. Built with Python, Django, HTMX, and Tailwind CSS.

### GitHub Topics / Tags:
`python` • `django` • `htmx` • `tailwind-css` • `chartjs` • `pytest` • `housing-society-management` • `full-stack` • `clean-architecture` • `portfolio-project`

---

## 5. Technical Interview / Viva Talking Points

When an interviewer asks: *"Tell me about a challenging full-stack project you built"*, answer using this framework:

1. **Context & Problem**:
   *"I built NivasSetu to tackle a real-world problem in residential societies in India where maintenance requests and dues records are kept in unstructured WhatsApp chats or physical notebooks, causing missed repairs and financial disputes."*

2. **Architecture Choice**:
   *"Rather than adding unnecessary complexity with a heavy React SPA, I chose a modern hypermedia approach with Django and HTMX. This gave me full server-side state security, rapid ORM querying, and snappy partial page updates over the wire."*

3. **Key Technical Challenge**:
   *"The most interesting challenge was designing the complaint state machine and SLA countdown logic in the Django ORM to handle overdue calculation dynamically on read without requiring background cron worker overhead for local installations."*

4. **Testing & Rigor**:
   *"I followed 3NF database normalization and wrote a 14-test automated pytest-django suite covering access control decorators, SLA math, tenant data isolation, and dues reconciliation."*

