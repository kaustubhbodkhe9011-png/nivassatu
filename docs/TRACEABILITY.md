# Requirement Traceability Matrix

**Project:** NivasSetu  **Version:** 1.0

> This matrix traces every functional requirement from the SRS to its database table, UML diagram, input form or view, output screen, and test case.

---

| Req ID | Requirement (brief) | DB Table(s) | UML Reference | View / Form | Output Page | Test Case |
|--------|--------------------|-----------|-----------|-----------|-----------|----|
| FR-01-1 | Login with username & password | accounts_user | Seq: Login flow | LoginView / LoginForm | Role dashboard | TC-01 |
| FR-01-2 | Redirect to role dashboard after login | accounts_user | Activity: Login | LoginView | Secretary/Resident/Staff dashboard | TC-01, TC-02 |
| FR-01-3 | Unauthenticated → login redirect | accounts_user | Use Case: Login | @login_required decorator | /accounts/login/ | TC-03 |
| FR-01-4 | Change password | accounts_user | Use Case | ChangePasswordView | Profile page | — |
| FR-01-5 | Three roles: SEC / RES / STAFF | accounts_user (role field) | Class diagram: User | UserRole enum | Dashboard dispatcher | TC-01 |
| FR-02-1 | Add buildings | society_building | ER: BUILDING | BuildingCreateView | Flat list | TC-04 |
| FR-02-2 | Add flats | society_flat | ER: FLAT | FlatCreateView / FlatForm | Flat list | TC-04 |
| FR-02-3 | Assign resident to flat | society_residentprofile | ER: RESIDENTPROFILE | AssignResidentView | Resident list | TC-05 |
| FR-02-4 | Owner / Tenant occupancy | society_residentprofile | ER: occupancy_type | ResidentProfile model | Resident list | TC-05 |
| FR-02-5 | Staff profile with trade | society_staffprofile | ER: STAFFPROFILE | StaffProfile model | Staff admin | TC-06 |
| FR-03-1 | Create complaint (category, priority, photo) | complaints_complaint | Activity: Raise complaint | CreateComplaintView / ComplaintForm | Complaint detail | TC-08 |
| FR-03-2 | Auto-generate ticket number | complaints_complaint | Seq: Raise complaint | Complaint.save() | Complaint detail header | TC-09 |
| FR-03-3 | Auto-calculate SLA deadline | complaints_complaint | State: SLA timer | Complaint.save() (SLA_HOURS dict) | Complaint detail SLA badge | TC-08 |
| FR-03-4 | Status workflow | complaints_complaint, complaints_complaintstatushistory | State diagram | UpdateStatusView | Complaint detail timeline | TC-09 |
| FR-03-5 | Resident reopen within 7 days | complaints_complaint | State: RESOLVED→OPEN | ReopenView / can_reopen property | Reopen button | TC-09 |
| FR-03-6 | Overdue flag | complaints_complaint | State: OVERDUE note | is_overdue property | Red badge on ticket | TC-08 |
| FR-03-7 | Secretary assigns staff | complaints_complaint | Seq: Assign & resolve | AssignStaffView | Complaint detail side panel | TC-10 |
| FR-03-8 | Staff updates status | complaints_complaint | Seq: Assign & resolve | UpdateStatusView | Timeline HTMX update | TC-10 |
| FR-03-9 | Comment thread | complaints_complaintcomment | Class: ComplaintComment | AddCommentView | Comment thread in detail | — |
| FR-03-10 | Status history | complaints_complaintstatushistory | Class: ComplaintStatusHistory | Auto-created on status change | Timeline | TC-09 |
| FR-03-11 | Star rating feedback | complaints_complaintfeedback | ER: COMPLAINTFEEDBACK | FeedbackView | Complaint detail footer | — |
| FR-04-1 | Create notice | notices_notice | ER: NOTICE | CreateNoticeView / NoticeForm | Notice list | TC-11 |
| FR-04-2 | Pin important notice | notices_notice (is_pinned) | Class: Notice | NoticeForm | Pinned notices section | TC-11 |
| FR-04-3 | Resident acknowledges notice | notices_noticeacknowledgement | ER: NOTICEACKNOWLEDGEMENT | AcknowledgeView | Notice list (HTMX) | TC-11 |
| FR-04-4 | Read-receipt count for secretary | notices_noticeacknowledgement | ER: cardinality 1:N | Secretary dashboard | Dashboard table | TC-11 |
| FR-05-1 | Define maintenance plan | dues_maintenanceplan | ER: MAINTENANCEPLAN | MaintenancePlan admin | Generate dues page | TC-12 |
| FR-05-2 | Generate dues per flat | dues_duesrecord | ER: DUESRECORD | GenerateDuesView | Dues list | TC-12 |
| FR-05-3 | Due = base + rate × sq_ft | dues_duesrecord | ER: amount_due | calculate_due_for_flat() | Dues list amount column | TC-12 |
| FR-05-4 | Record manual payment | dues_payment | ER: PAYMENT | RecordPaymentView / PaymentForm | Dues list status update | TC-12 |
| FR-05-5 | Auto-generate receipt number | dues_payment | ER: receipt_number | Payment.save() | Receipt page header | TC-12 |
| FR-05-6 | Resident views own dues | dues_duesrecord | — | DuesListView (filtered) | Dues list (resident view) | TC-12 |
| FR-05-7 | Printable receipt | dues_payment | — | ReceiptView | Receipt page | TC-12 |
| FR-06-1 | Secretary dashboard summary cards | complaints_complaint, dues_duesrecord | — | SecretaryDashboardView | Dashboard cards | TC-13 |
| FR-06-2 | Ticket status doughnut chart | complaints_complaint | — | ReportsView | Reports page chart | TC-13 |
| FR-06-3 | Average resolution time | complaints_complaintstatushistory | — | ReportsView | Reports stat card | TC-13 |
| FR-06-4 | Top 5 categories | complaints_complaint, complaints_complaintcategory | — | ReportsView | Reports bar section | TC-13 |
| FR-06-5 | Export complaints CSV | complaints_complaint | — | ExportComplaintsCSV | Downloaded .csv file | TC-14 |
| FR-06-6 | Export dues CSV | dues_duesrecord | — | ExportDuesCSV | Downloaded .csv file | TC-14 |
| FR-07-1 | Audit log on key actions | audit_auditlog | ER: AUDITLOG | record_audit() util | Audit trail page | TC-13 |
| FR-07-2 | Audit entry fields | audit_auditlog | Class: AuditLog | AuditLog model | Audit trail table columns | TC-13 |
| FR-07-3 | Secretary-only audit view | audit_auditlog | Use Case: Secretary | @secretary_required decorator | Audit trail page | TC-14 |
| FR-08-1 | Complaint list HTMX filters | complaints_complaint | DFD 2.0 | ComplaintListView / HTMX | Ticket table partial | TC-07 |
| FR-08-2 | HTMX partial update | (all) | Seq diagram | hx-target on forms | Only table updates, not page | TC-07 |

---

## Notes

- **TC-01** = `test_accounts.py::test_user_roles`
- **TC-02** = `test_accounts.py::test_login_redirect_by_role`
- **TC-03** = `test_accounts.py::test_unauthenticated_redirect`
- **TC-04** = `test_society.py::test_flat_naming`
- **TC-05** = `test_society.py::test_occupancy_types`
- **TC-06** = `test_society.py::test_staff_profile`
- **TC-07** = `test_society.py::test_secretary_access_control`
- **TC-08** = `test_complaints.py::test_complaint_sla`
- **TC-09** = `test_complaints.py::test_complaint_state_machine`
- **TC-10** = `test_complaints.py::test_resident_isolation`
- **TC-11** = `test_notices.py::test_notice_and_acknowledgement`
- **TC-12** = `test_dues.py::test_dues_and_payment`
- **TC-13** = `test_reports.py::test_audit_logging`
- **TC-14** = `test_reports.py::test_csv_exports`

