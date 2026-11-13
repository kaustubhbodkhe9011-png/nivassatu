# Chapter 4 — System Design

**Project:** NivasSetu  **Version:** 1.0

---

## 4.1 Architecture Overview

NivasSetu follows a classic **3-tier web architecture**:

```
┌──────────────────────────────────────────────────────────┐
│  Presentation Tier (Browser)                             │
│  Django Templates + Tailwind CSS + HTMX + Chart.js       │
└─────────────────────────┬────────────────────────────────┘
                          │  HTTP / HTMX (partial)
┌─────────────────────────▼────────────────────────────────┐
│  Application Tier (Django)                               │
│  URLs → Views → Forms → Models (ORM) → Serializers       │
│  Middleware: Auth, CSRF, Messages, Session               │
└─────────────────────────┬────────────────────────────────┘
                          │  SQL queries via ORM
┌─────────────────────────▼────────────────────────────────┐
│  Data Tier                                               │
│  SQLite (dev) / PostgreSQL (prod)                        │
└──────────────────────────────────────────────────────────┘
```

**Key design decisions:**
- HTMX delivers partial HTML fragments (e.g., filtered ticket table) without JSON APIs
- No JavaScript framework; interactivity comes from HTMX + Alpine.js-style `x-data` toggle for dark mode
- One Django project, eight apps, each owns its models/views/urls/templates

---

## 4.2 Context Diagram (DFD Level 0)

```mermaid
flowchart LR
    Secretary(["👤 Secretary"])
    Resident(["👤 Resident"])
    Staff(["👤 Staff"])
    SYS["NivasSetu\nSystem"]

    Secretary -- "Login, Manage flats/residents/staff\nAssign complaints, Record payments\nCreate notices, View reports" --> SYS
    Resident -- "Login, Raise complaints\nView notices, View dues\nGive feedback" --> SYS
    Staff -- "Login, View assigned tickets\nUpdate status with remarks" --> SYS

    SYS -- "Dashboards, Ticket lists\nNotices, Dues records\nReceipts, Reports, Audit log" --> Secretary
    SYS -- "Dashboard, Complaint status\nNotices, Dues history, Receipt" --> Resident
    SYS -- "Assigned ticket list\nTicket detail" --> Staff
```

---

## 4.3 DFD Level 1 — System Processes

```mermaid
flowchart TD
    U_S(["Secretary"])
    U_R(["Resident"])
    U_T(["Staff"])

    P1["1.0\nAuthenticate\nUsers"]
    P2["2.0\nManage Society\nSetup"]
    P3["3.0\nHandle\nComplaints"]
    P4["4.0\nPublish\nNotices"]
    P5["5.0\nManage Dues\n& Payments"]
    P6["6.0\nGenerate\nReports"]
    P7["7.0\nRecord\nAudit Log"]

    DS1[("User Store")]
    DS2[("Society/Flat Store")]
    DS3[("Complaint Store")]
    DS4[("Notice Store")]
    DS5[("Dues/Payment Store")]
    DS6[("Audit Store")]

    U_S --> P1 --> DS1
    U_R --> P1
    U_T --> P1
    U_S --> P2 --> DS2
    U_R --> P3
    U_S --> P3
    U_T --> P3
    P3 <--> DS3
    U_S --> P4 --> DS4
    U_R -- "Acknowledge" --> P4
    U_S --> P5 --> DS5
    U_R -- "View dues" --> P5
    U_S --> P6
    P6 --> DS3
    P6 --> DS5
    P3 --> P7
    P5 --> P7
    P4 --> P7
    P7 --> DS6
```

---

## 4.4 DFD Level 2 — Complaint Process (Process 3.0)

```mermaid
flowchart TD
    R(["Resident"])
    S(["Secretary"])
    T(["Staff"])

    P31["3.1 Create\nComplaint"]
    P32["3.2 Validate &\nAuto-assign Ticket No"]
    P33["3.3 Assign\nStaff"]
    P34["3.4 Update\nStatus"]
    P35["3.5 Add\nComment"]
    P36["3.6 Submit\nFeedback"]
    P37["3.7 Check\nSLA / Overdue"]

    DS_C[("Complaint\nTable")]
    DS_H[("Status History\nTable")]
    DS_CMT[("Comment\nTable")]
    DS_FB[("Feedback\nTable")]

    R --> P31 --> P32 --> DS_C
    P32 --> DS_H
    P32 --> P37
    P37 -- "flag overdue" --> DS_C
    DS_C --> P33
    S --> P33 --> DS_C
    P33 --> DS_H
    T --> P34 --> DS_C
    P34 --> DS_H
    R --> P35
    S --> P35
    T --> P35
    P35 --> DS_CMT
    R --> P36 --> DS_FB
```

---

## 4.5 Use Case Diagram

```mermaid
flowchart LR
    Secretary(["👤 Secretary"])
    Resident(["👤 Resident"])
    Staff(["👤 Staff"])

    subgraph NivasSetu
        UC1["Login / Logout"]
        UC2["Change Password"]
        UC3["View Dashboard"]
        UC4["Manage Buildings & Flats"]
        UC5["Manage Residents & Staff"]
        UC6["Create Complaint"]
        UC7["View Complaint List"]
        UC8["Assign Staff to Complaint"]
        UC9["Update Complaint Status"]
        UC10["Add Comment"]
        UC11["Submit Feedback"]
        UC12["Reopen Complaint"]
        UC13["Create Notice"]
        UC14["Acknowledge Notice"]
        UC15["Generate Dues"]
        UC16["Record Payment"]
        UC17["View Receipt"]
        UC18["View Reports"]
        UC19["Export CSV"]
        UC20["View Audit Trail"]
    end

    Secretary --> UC1
    Resident --> UC1
    Staff --> UC1
    Secretary --> UC2
    Resident --> UC2
    Staff --> UC2
    Secretary --> UC3
    Resident --> UC3
    Staff --> UC3
    Secretary --> UC4
    Secretary --> UC5
    Resident --> UC6
    Secretary --> UC7
    Resident --> UC7
    Staff --> UC7
    Secretary --> UC8
    Staff --> UC9
    Secretary --> UC9
    Secretary --> UC10
    Resident --> UC10
    Staff --> UC10
    Resident --> UC11
    Resident --> UC12
    Secretary --> UC13
    Resident --> UC14
    Secretary --> UC15
    Secretary --> UC16
    Resident --> UC17
    Secretary --> UC17
    Secretary --> UC18
    Secretary --> UC19
    Secretary --> UC20
```

---

## 4.6 Class Diagram (Core Models)

```mermaid
classDiagram
    class User {
        +int id
        +str username
        +str role
        +str phone_number
        +bool is_secretary()
        +bool is_resident()
        +bool is_staff_member()
    }
    class Building {
        +int id
        +str name
        +Society society
    }
    class Flat {
        +int id
        +str flat_number
        +int floor
        +str flat_type
        +Decimal square_feet
        +Building building
    }
    class ResidentProfile {
        +User user
        +Flat flat
        +str occupancy_type
        +date move_in_date
    }
    class StaffProfile {
        +User user
        +str trade
        +str phone
    }
    class Complaint {
        +int id
        +str ticket_number
        +str status
        +str priority
        +text description
        +datetime sla_deadline
        +bool is_overdue()
        +bool can_reopen()
        +save()
    }
    class ComplaintStatusHistory {
        +Complaint complaint
        +User changed_by
        +str old_status
        +str new_status
        +str remark
        +datetime changed_at
    }
    class ComplaintComment {
        +Complaint complaint
        +User author
        +text body
        +datetime created_at
    }
    class ComplaintFeedback {
        +Complaint complaint
        +User resident
        +int rating
        +text comment
    }
    class Notice {
        +int id
        +str title
        +text body
        +bool is_pinned
    }
    class NoticeAcknowledgement {
        +Notice notice
        +User resident
        +datetime read_at
    }
    class MaintenancePlan {
        +Decimal base_charge
        +Decimal rate_per_sqft
        +int month
        +int year
        +calculate_due_for_flat(flat)
    }
    class DuesRecord {
        +MaintenancePlan plan
        +Flat flat
        +Decimal amount_due
        +Decimal amount_paid
        +str status
    }
    class Payment {
        +DuesRecord dues_record
        +str receipt_number
        +Decimal amount
        +str mode
        +str reference
    }
    class AuditLog {
        +User actor
        +str action
        +str target_description
        +text before_value
        +text after_value
        +datetime timestamp
    }

    User "1" --> "0..1" ResidentProfile : has
    User "1" --> "0..1" StaffProfile : has
    Building "1" --> "N" Flat : contains
    Flat "1" --> "N" ResidentProfile : occupied by
    Flat "1" --> "N" Complaint : from
    User "1" --> "N" Complaint : raises
    User "1" --> "N" Complaint : assigned to
    Complaint "1" --> "N" ComplaintStatusHistory : records
    Complaint "1" --> "N" ComplaintComment : has
    Complaint "1" --> "0..1" ComplaintFeedback : receives
    Notice "1" --> "N" NoticeAcknowledgement : acknowledged by
    MaintenancePlan "1" --> "N" DuesRecord : generates
    Flat "1" --> "N" DuesRecord : billed to
    DuesRecord "1" --> "N" Payment : paid via
```

---

## 4.7 Activity Diagram — Raise a Complaint

```mermaid
flowchart TD
    Start([Start]) --> Login
    Login["Resident logs in"] --> Dashboard
    Dashboard["Resident Dashboard"] --> ClickRaise
    ClickRaise["Clicks 'Raise Complaint'"] --> FillForm
    FillForm["Fill form: category, description,\npriority, optional photo"] --> Submit
    Submit["Submit form (POST)"] --> Validate{Valid?}
    Validate -- No --> ShowErrors["Show validation errors\non form"]
    ShowErrors --> FillForm
    Validate -- Yes --> SaveDB["Save Complaint to DB\nauto-generate ticket number\nauto-calculate SLA deadline"]
    SaveDB --> SaveHistory["Create status history entry\n(OPEN, actor = resident)"]
    SaveHistory --> AuditEntry["Create AuditLog entry"]
    AuditEntry --> Toast["Show success toast\nwith ticket number"]
    Toast --> DetailPage["Redirect to complaint detail page"]
    DetailPage --> End([End])
```

---

## 4.8 Sequence Diagram — Raise a Complaint

```mermaid
sequenceDiagram
    actor Resident
    participant Browser
    participant ComplaintsView
    participant ComplaintModel
    participant AuditUtil
    participant DB

    Resident->>Browser: Click "Raise Complaint"
    Browser->>ComplaintsView: GET /complaints/create/
    ComplaintsView->>Browser: Render empty form

    Resident->>Browser: Fill form & submit
    Browser->>ComplaintsView: POST /complaints/create/
    ComplaintsView->>ComplaintsView: Validate ComplaintForm
    ComplaintsView->>ComplaintModel: complaint.save()
    ComplaintModel->>DB: INSERT complaints_complaint
    ComplaintModel->>DB: INSERT status_history (OPEN)
    ComplaintsView->>AuditUtil: record_audit(actor, "COMPLAINT_CREATED", ...)
    AuditUtil->>DB: INSERT audit_auditlog
    ComplaintsView->>Browser: HTTP 302 redirect to detail
    Browser->>ComplaintsView: GET /complaints/<id>/
    ComplaintsView->>Browser: Render complaint detail with toast
```

---

## 4.9 Sequence Diagram — Secretary Assigns Staff and Staff Resolves

```mermaid
sequenceDiagram
    actor Secretary
    actor Staff
    participant Browser
    participant ComplaintsView
    participant DB

    Secretary->>Browser: Open complaint detail
    Browser->>ComplaintsView: GET /complaints/<id>/
    ComplaintsView->>Browser: Render detail with assign panel

    Secretary->>Browser: Select staff, click Assign
    Browser->>ComplaintsView: POST /complaints/<id>/assign/
    ComplaintsView->>DB: UPDATE complaint assigned_to, status=ASSIGNED
    ComplaintsView->>DB: INSERT status_history (ASSIGNED)
    ComplaintsView->>Browser: HTMX partial — updated status badge

    Staff->>Browser: Open assigned complaint
    Browser->>ComplaintsView: GET /complaints/<id>/
    Staff->>Browser: Select "In Progress", add remark, submit
    Browser->>ComplaintsView: POST /complaints/<id>/status/
    ComplaintsView->>DB: UPDATE complaint status=IN_PROGRESS
    ComplaintsView->>DB: INSERT status_history (IN_PROGRESS)
    ComplaintsView->>Browser: HTMX partial — updated timeline

    Staff->>Browser: Select "Resolved", add remark, submit
    Browser->>ComplaintsView: POST /complaints/<id>/status/
    ComplaintsView->>DB: UPDATE complaint status=RESOLVED
    ComplaintsView->>DB: INSERT status_history (RESOLVED)
    ComplaintsView->>Browser: HTMX partial — resolved timeline
```

---

## 4.10 State Diagram — Complaint Lifecycle

```mermaid
stateDiagram-v2
    [*] --> OPEN : Resident raises complaint

    OPEN --> ASSIGNED : Secretary assigns staff
    ASSIGNED --> IN_PROGRESS : Staff starts work
    IN_PROGRESS --> RESOLVED : Staff marks resolved
    RESOLVED --> CLOSED : Secretary or auto-close after 7 days
    RESOLVED --> OPEN : Resident reopens within 7 days

    OPEN --> CLOSED : Secretary closes directly
    ASSIGNED --> CLOSED : Secretary closes
    IN_PROGRESS --> CLOSED : Secretary closes

    CLOSED --> [*]

    note right of OPEN : SLA timer starts\nOverdue flag set if deadline passed
    note right of RESOLVED : 7-day reopen window\nFeedback can be submitted
```

