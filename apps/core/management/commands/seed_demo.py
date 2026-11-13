"""
Management command to seed realistic synthetic demo data.
Includes 1 Society, 2 Buildings, 30 Flats, 3 Staff, 10 Residents, 40 Complaints, Notices, and Dues.
All names, numbers and phones are completely fictional demo data.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

from apps.accounts.models import User, UserRole
from apps.society.models import Society, Building, Flat, FlatType, ResidentProfile, OccupancyType, StaffProfile
from apps.complaints.models import ComplaintCategory, Complaint, ComplaintStatus, Priority, ComplaintStatusHistory, ComplaintComment, ComplaintFeedback
from apps.notices.models import Notice, NoticeCategory, NoticeAcknowledgement
from apps.dues.models import MaintenancePlan, DuesRecord, Payment, DuesStatus, PaymentMode
from apps.audit.models import AuditLog, AuditAction


class Command(BaseCommand):
    help = "Populate database with synthetic, realistic housing society demo data"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Clearing existing demo records..."))
        ComplaintFeedback.objects.all().delete()
        ComplaintComment.objects.all().delete()
        ComplaintStatusHistory.objects.all().delete()
        Complaint.objects.all().delete()
        NoticeAcknowledgement.objects.all().delete()
        Notice.objects.all().delete()
        Payment.objects.all().delete()
        DuesRecord.objects.all().delete()
        ResidentProfile.objects.all().delete()
        StaffProfile.objects.all().delete()
        Flat.objects.all().delete()
        Building.objects.all().delete()
        Society.objects.all().delete()
        ComplaintCategory.objects.all().delete()
        MaintenancePlan.objects.all().delete()
        AuditLog.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        self.stdout.write("1. Creating Society & Maintenance Plan...")
        soc = Society.objects.create(
            name="Nivas Residences CHS",
            registration_number="MH/MUM/CHS/2026/7412",
            address="Plot 12, Nivas Greens Boulevard, Off Western Express Highway, Goregaon East, Mumbai, Maharashtra 400063",
            contact_phone="+91 9000000001",
            contact_email="secretary@nivasresidences.demo",
        )

        plan = MaintenancePlan.objects.create(
            name="Standard Residential Tariff",
            base_rate_per_sqft=Decimal("2.50"),
            fixed_charge=Decimal("750.00"),
            late_fine_rate=Decimal("150.00"),
        )

        self.stdout.write("2. Creating Core Users & Staff...")
        sec_user = User.objects.create_user(
            username="secretary",
            email="secretary@nivasresidences.demo",
            password="admin123",
            role=UserRole.SECRETARY,
            first_name="Vikramaditya",
            last_name="Kulkarni",
            phone_number="+91 9000000001",
        )

        staff_data = [
            ("staff1", "staff123", "Dinesh", "Wankhede", "Electrician", "STF-EL-01", "+91 9000000011"),
            ("staff2", "staff123", "Santosh", "Rao", "Plumber", "STF-PL-02", "+91 9000000012"),
            ("staff3", "staff123", "Nitin", "Salunkhe", "Lift & Elevator", "STF-LF-03", "+91 9000000013"),
        ]
        staff_objs = []
        for uname, pwd, fname, lname, spec, code, ph in staff_data:
            u = User.objects.create_user(
                username=uname,
                password=pwd,
                role=UserRole.STAFF,
                first_name=fname,
                last_name=lname,
                phone_number=ph
            )
            sp = StaffProfile.objects.create(user=u, employee_code=code, specialty=spec, is_available=True)
            staff_objs.append(sp)

        self.stdout.write("3. Creating Wings and 30 Flats...")
        wing_a = Building.objects.create(society=soc, name="Wing A", total_floors=5)
        wing_b = Building.objects.create(society=soc, name="Wing B", total_floors=5)

        flats = []
        # Wing A: 15 flats (3 flats per floor across 5 floors)
        for flr in range(1, 6):
            for unit in range(1, 4):
                f_num = f"{flr}0{unit}"
                sqft = Decimal("750.00") if unit == 1 else (Decimal("950.00") if unit == 2 else Decimal("1200.00"))
                ftype = FlatType.ONE_BHK if unit == 1 else (FlatType.TWO_BHK if unit == 2 else FlatType.THREE_BHK)
                flats.append(Flat.objects.create(building=wing_a, flat_number=f_num, floor=flr, flat_type=ftype, square_feet=sqft))

        # Wing B: 15 flats
        for flr in range(1, 6):
            for unit in range(1, 4):
                f_num = f"{flr}0{unit}"
                sqft = Decimal("800.00") if unit == 1 else (Decimal("1050.00") if unit == 2 else Decimal("1350.00"))
                ftype = FlatType.ONE_BHK if unit == 1 else (FlatType.TWO_BHK if unit == 2 else FlatType.THREE_BHK)
                flats.append(Flat.objects.create(building=wing_b, flat_number=f_num, floor=flr, flat_type=ftype, square_feet=sqft))

        self.stdout.write("4. Creating Resident Profiles...")
        resident_names = [
            ("resident1", "resident123", "Arjun", "Sen", OccupancyType.OWNER),
            ("resident2", "resident123", "Neha", "Kulkarni", OccupancyType.OWNER),
            ("resident3", "resident123", "Rajeshwar", "Nair", OccupancyType.OWNER),
            ("resident4", "resident123", "Pooja", "Sharma", OccupancyType.TENANT),
            ("resident5", "resident123", "Anand", "Varma", OccupancyType.OWNER),
            ("resident6", "resident123", "Meera", "Merchant", OccupancyType.OWNER),
            ("resident7", "resident123", "Farhan", "Qureshi", OccupancyType.TENANT),
            ("resident8", "resident123", "Kavita", "Reddy", OccupancyType.OWNER),
            ("resident9", "resident123", "Sanjay", "Chawla", OccupancyType.OWNER),
            ("resident10", "resident123", "Aditi", "Joshi", OccupancyType.TENANT),
        ]
        residents = []
        for i, (uname, pwd, fname, lname, occ) in enumerate(resident_names):
            u = User.objects.create_user(
                username=uname,
                password=pwd,
                role=UserRole.RESIDENT,
                first_name=fname,
                last_name=lname,
                phone_number=f"+91 90000000{20+i}"
            )
            assigned_flat = flats[i]
            ResidentProfile.objects.create(
                user=u,
                flat=assigned_flat,
                occupancy_type=occ,
                move_in_date=timezone.now().date() - timedelta(days=random.randint(60, 400)),
                is_active=True
            )
            residents.append((u, assigned_flat))

        self.stdout.write("5. Creating Categories & 40 Realistic Complaints...")
        cat_plumbing = ComplaintCategory.objects.create(name="Plumbing & Water", description="Leaking pipes, low water pressure, tap failure", default_sla_hours=24)
        cat_electric = ComplaintCategory.objects.create(name="Electrical & Wiring", description="MCB trip, hallway light burnout, earthing fault", default_sla_hours=12)
        cat_lift = ComplaintCategory.objects.create(name="Lift & Elevators", description="Passenger lift stuck, door sensor malfunction", default_sla_hours=12)
        cat_security = ComplaintCategory.objects.create(name="Security & Parking", description="Boom barrier stuck, unauthorized parking, CCTV outage", default_sla_hours=48)
        cat_clean = ComplaintCategory.objects.create(name="Cleanliness & Waste", description="Garbage chute blocked, staircase cleaning pending", default_sla_hours=24)
        cat_civil = ComplaintCategory.objects.create(name="Civil & Structural", description="Plaster peeling off, terrace waterproofing leakage", default_sla_hours=72)
        categories = [cat_plumbing, cat_electric, cat_lift, cat_security, cat_clean, cat_civil]

        sample_titles = [
            ("Continuous water leakage in master bedroom washroom", cat_plumbing, Priority.HIGH),
            ("Corridor tube light blinking on 3rd floor", cat_electric, Priority.LOW),
            ("Lift B jerk during stopping on 4th floor", cat_lift, Priority.URGENT),
            ("Unknown car parked in designated slot A-102", cat_security, Priority.MEDIUM),
            ("Wet garbage bin overflowing near staircase", cat_clean, Priority.HIGH),
            ("Ceiling seepage from terrace during heavy showers", cat_civil, Priority.MEDIUM),
            ("Main water inlet valve knob broken", cat_plumbing, Priority.URGENT),
            ("Power trip in kitchen circuit whenever microwave starts", cat_electric, Priority.HIGH),
            ("Lift intercom phone disconnected", cat_lift, Priority.HIGH),
            ("Dry waste not collected for 2 days", cat_clean, Priority.LOW),
        ]

        # Generate 40 complaints across time
        for idx in range(1, 41):
            title, cat, prio = random.choice(sample_titles)
            user, flat = random.choice(residents)
            status_pool = [ComplaintStatus.OPEN, ComplaintStatus.ASSIGNED, ComplaintStatus.IN_PROGRESS, ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED]
            status = random.choice(status_pool)
            days_ago = random.randint(1, 25)

            comp = Complaint.objects.create(
                raised_by=user,
                flat=flat,
                category=cat,
                title=f"{title} (Unit {flat.flat_number})",
                description=f"Detailed inspection requested: {title}. Resident available on phone during evenings.",
                priority=prio,
                status=status,
                assigned_to=random.choice(staff_objs) if status != ComplaintStatus.OPEN else None,
                created_at=timezone.now() - timedelta(days=days_ago)
            )

            # Add comments
            ComplaintComment.objects.create(
                complaint=comp,
                author=user,
                comment="Reported via NivasSetu portal."
            )
            if comp.assigned_to:
                ComplaintComment.objects.create(
                    complaint=comp,
                    author=comp.assigned_to.user,
                    comment="Inspected the unit. Spares requested from stores.",
                    is_internal=True
                )

            # If resolved/closed, optionally add feedback
            if status in [ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED]:
                comp.resolved_at = timezone.now() - timedelta(days=random.randint(0, days_ago))
                comp.save()
                if random.choice([True, False]):
                    ComplaintFeedback.objects.create(
                        complaint=comp,
                        resident=user,
                        rating=random.randint(3, 5),
                        remarks="Issue resolved promptly by technician."
                    )

        self.stdout.write("6. Publishing Notices...")
        n1 = Notice.objects.create(
            published_by=sec_user,
            title="Half-Day Water Supply Shutdown for Overhead Tank Cleaning",
            category=NoticeCategory.MAINTENANCE,
            content="Dear Residents,\nOverhead water tanks of Wing A and Wing B will undergo biannual chemical cleaning this Saturday from 9:00 AM to 2:00 PM. Please store sufficient potable water in advance.",
            is_pinned=True,
        )
        Notice.objects.create(
            published_by=sec_user,
            title="Annual General Body Meeting (AGM) Notice & Agenda",
            category=NoticeCategory.MEETING,
            content="Notice is hereby given that the 14th AGM of Nivas Residences CHS will be held in the Clubhouse on Sunday at 10:30 AM. Agenda covers statutory audit report and lift modernization tenders.",
            is_pinned=True,
        )
        Notice.objects.create(
            published_by=sec_user,
            title="Diwali Community Illumination & Rangoli Competition",
            category=NoticeCategory.CELEBRATION,
            content="Society cultural committee cordially invites all families to participate in the traditional lantern and rangoli gathering in the central podium garden this weekend.",
            is_pinned=False,
        )

        # Acknowledgements
        for u, _ in residents[:5]:
            NoticeAcknowledgement.objects.create(notice=n1, user=u)

        self.stdout.write("7. Generating Maintenance Dues & Receipts...")
        current_month = timezone.now().strftime("%B %Y")
        due_date = timezone.now().date() + timedelta(days=15)

        for flat in flats:
            amount = plan.calculate_due_for_flat(flat)
            due_rec = DuesRecord.objects.create(
                flat=flat,
                plan=plan,
                billing_month=current_month,
                principal_amount=amount,
                total_due=amount,
                due_date=due_date,
                status=DuesStatus.PENDING
            )
            # Settle payments for first 20 flats
            if random.random() < 0.70:
                p_user = flat.get_current_occupant() or sec_user
                Payment.objects.create(
                    dues_record=due_rec,
                    recorded_by=p_user,
                    amount=amount,
                    payment_mode=random.choice([PaymentMode.UPI, PaymentMode.CHEQUE, PaymentMode.CASH]),
                    transaction_reference=f"UTR{random.randint(100000000, 999999999)}",
                    payment_date=timezone.now().date() - timedelta(days=random.randint(1, 10)),
                    remarks="Dues paid in full against bill."
                )

        self.stdout.write("8. Creating Audit Logs...")
        AuditLog.objects.create(
            actor=sec_user,
            action=AuditAction.CREATE,
            target_model="Society",
            target_object_id=str(soc.id),
            summary="Society initialized with master tariff plan.",
            ip_address="127.0.0.1"
        )
        AuditLog.objects.create(
            actor=sec_user,
            action=AuditAction.STATUS_CHANGE,
            target_model="DuesRecord",
            target_object_id="All",
            summary=f"Batch generated maintenance bills for {current_month}.",
            ip_address="127.0.0.1"
        )

        self.stdout.write(self.style.SUCCESS("✓ Seed complete! Realistic demo dataset created successfully."))
        self.stdout.write(self.style.SUCCESS("Demo logins: [secretary / admin123], [resident1 / resident123], [staff1 / staff123]"))

