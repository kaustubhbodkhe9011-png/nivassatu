from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Complaint, ComplaintCategory, ComplaintStatus, ComplaintStatusHistory, ComplaintComment, ComplaintFeedback
from .forms import ComplaintForm, AssignStaffForm, ComplaintCommentForm, ComplaintFeedbackForm
from apps.society.models import ResidentProfile

@login_required
def complaint_list_view(request):
    """
    Role-filtered complaint directory with search and multi-facet filtering.
    Secretary: Sees all tickets across society.
    Staff: Sees assigned tickets.
    Resident: Sees only tickets raised by them or for their occupied flat.
    """
    user = request.user
    if user.is_secretary:
        qs = Complaint.objects.select_related("raised_by", "flat__building", "category", "assigned_to__user").all()
    elif user.is_staff_member:
        qs = Complaint.objects.filter(assigned_to__user=user).select_related("raised_by", "flat__building", "category")
    else:
        # Resident: own raised or flats they occupy
        occupied_flats = user.resident_profiles.filter(is_active=True).values_list("flat_id", flat=True)
        qs = Complaint.objects.filter(Q(raised_by=user) | Q(flat_id__in=occupied_flats)).select_related("raised_by", "flat__building", "category", "assigned_to__user")

    # Filters
    status_filter = request.GET.get("status")
    priority_filter = request.GET.get("priority")
    category_filter = request.GET.get("category")
    search_query = request.GET.get("q")

    if status_filter:
        qs = qs.filter(status=status_filter)
    if priority_filter:
        qs = qs.filter(priority=priority_filter)
    if category_filter:
        qs = qs.filter(category_id=category_filter)
    if search_query:
        qs = qs.filter(
            Q(ticket_number__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    categories = ComplaintCategory.objects.filter(is_active=True)

    # Return partial template if requested via HTMX
    if request.headers.get("HX-Request"):
        return render(request, "complaints/partials/ticket_table.html", {"complaints": qs})

    return render(request, "complaints/complaint_list.html", {
        "complaints": qs,
        "categories": categories,
        "status_choices": ComplaintStatus.choices,
        "selected_status": status_filter,
        "selected_priority": priority_filter,
        "selected_category": category_filter,
        "search_query": search_query,
    })

@login_required
def create_complaint_view(request):
    """Allows a resident (or secretary) to lodge a new complaint ticket."""
    active_profile = request.user.resident_profiles.filter(is_active=True).select_related("flat").first()
    if not active_profile and not request.user.is_secretary:
        messages.error(request, "You must be assigned to an active flat unit before raising grievances.")
        return redirect("core:resident_dashboard")

    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.raised_by = request.user
            complaint.flat = active_profile.flat if active_profile else None
            if not complaint.flat and request.user.is_secretary:
                # Fallback to first flat for admin testing if not assigned
                from apps.society.models import Flat
                complaint.flat = Flat.objects.first()

            complaint.save()
            messages.success(request, f"Complaint {complaint.ticket_number} created successfully with SLA tracking.")
            return redirect("complaints:detail", ticket_number=complaint.ticket_number)
    else:
        form = ComplaintForm()

    return render(request, "complaints/create_complaint.html", {
        "form": form,
        "active_flat": active_profile.flat if active_profile else None
    })

@login_required
def complaint_detail_view(request, ticket_number):
    """Displays ticket details, timeline history, comments, and action buttons."""
    complaint = get_object_or_404(
        Complaint.objects.select_related("raised_by", "flat__building", "category", "assigned_to__user", "feedback"),
        ticket_number=ticket_number
    )
    
    # Permission verification
    user = request.user
    if not user.is_secretary and not (user.is_staff_member and complaint.assigned_to and complaint.assigned_to.user == user):
        user_flats = user.resident_profiles.values_list("flat_id", flat=True)
        if complaint.raised_by != user and complaint.flat_id not in user_flats:
            messages.error(request, "You do not have permission to view that grievance.")
            return redirect("complaints:list")

    assign_form = AssignStaffForm() if user.is_secretary else None
    comment_form = ComplaintCommentForm()
    feedback_form = ComplaintFeedbackForm() if (user == complaint.raised_by and complaint.status == ComplaintStatus.RESOLVED and not hasattr(complaint, "feedback")) else None

    comments = complaint.comments.select_related("author").all()
    if not (user.is_secretary or user.is_staff_member):
        comments = comments.filter(is_internal=False)

    return render(request, "complaints/complaint_detail.html", {
        "complaint": complaint,
        "history": complaint.status_history.select_related("changed_by").all(),
        "comments": comments,
        "assign_form": assign_form,
        "comment_form": comment_form,
        "feedback_form": feedback_form,
    })

@login_required
def assign_staff_view(request, ticket_number):
    """Secretary action: assign staff member and transition status to ASSIGNED."""
    if not request.user.is_secretary:
        messages.error(request, "Only the secretary can assign technicians.")
        return redirect("complaints:detail", ticket_number=ticket_number)

    complaint = get_object_or_404(Complaint, ticket_number=ticket_number)
    if request.method == "POST":
        form = AssignStaffForm(request.POST)
        if form.is_valid():
            staff = form.cleaned_data["staff_member"]
            remarks = form.cleaned_data.get("remarks") or f"Assigned to {staff.user.get_full_name() or staff.user.username} ({staff.specialty})"
            
            old_status = complaint.status
            complaint.assigned_to = staff
            complaint.status = ComplaintStatus.ASSIGNED
            complaint.save()

            ComplaintStatusHistory.objects.create(
                complaint=complaint,
                changed_by=request.user,
                from_status=old_status,
                to_status=ComplaintStatus.ASSIGNED,
                remarks=remarks
            )
            messages.success(request, f"Ticket assigned to {staff.user.get_full_name() or staff.user.username}.")
    return redirect("complaints:detail", ticket_number=ticket_number)

@login_required
def update_status_view(request, ticket_number):
    """Updates ticket status along the state machine (IN_PROGRESS, RESOLVED, CLOSED, REOPENED)."""
    complaint = get_object_or_404(Complaint, ticket_number=ticket_number)
    target_status = request.POST.get("target_status")
    remarks = request.POST.get("remarks", "").strip()

    old_status = complaint.status

    if target_status == ComplaintStatus.IN_PROGRESS and (request.user.is_staff_member or request.user.is_secretary):
        complaint.status = ComplaintStatus.IN_PROGRESS
    elif target_status == ComplaintStatus.RESOLVED and (request.user.is_staff_member or request.user.is_secretary):
        complaint.status = ComplaintStatus.RESOLVED
        complaint.resolved_at = timezone.now()
    elif target_status == ComplaintStatus.CLOSED and (request.user == complaint.raised_by or request.user.is_secretary):
        complaint.status = ComplaintStatus.CLOSED
        complaint.closed_at = timezone.now()
    elif target_status == ComplaintStatus.REOPENED and (request.user == complaint.raised_by or request.user.is_secretary):
        if not complaint.can_reopen:
            messages.error(request, "Ticket can only be reopened within 7 days of resolution.")
            return redirect("complaints:detail", ticket_number=ticket_number)
        complaint.status = ComplaintStatus.REOPENED
        complaint.reopened_at = timezone.now()
    else:
        messages.error(request, "Invalid status transition or insufficient permissions.")
        return redirect("complaints:detail", ticket_number=ticket_number)

    complaint.save()
    ComplaintStatusHistory.objects.create(
        complaint=complaint,
        changed_by=request.user,
        from_status=old_status,
        to_status=complaint.status,
        remarks=remarks or f"Status changed to {complaint.get_status_display()}."
    )
    messages.success(request, f"Ticket status updated to {complaint.get_status_display()}.")
    return redirect("complaints:detail", ticket_number=ticket_number)

@login_required
def add_comment_view(request, ticket_number):
    """Adds a message/comment to the ticket timeline."""
    complaint = get_object_or_404(Complaint, ticket_number=ticket_number)
    if request.method == "POST":
        form = ComplaintCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.complaint = complaint
            comment.author = request.user
            # Residents cannot mark comments as internal
            if not (request.user.is_secretary or request.user.is_staff_member):
                comment.is_internal = False
            comment.save()
            messages.success(request, "Comment posted.")
    return redirect("complaints:detail", ticket_number=ticket_number)

@login_required
def submit_feedback_view(request, ticket_number):
    """Collects 1-to-5 star rating and feedback from resident."""
    complaint = get_object_or_404(Complaint, ticket_number=ticket_number)
    if request.user != complaint.raised_by:
        messages.error(request, "Only the resident who raised the grievance can submit feedback.")
        return redirect("complaints:detail", ticket_number=ticket_number)

    if request.method == "POST":
        form = ComplaintFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.complaint = complaint
            feedback.resident = request.user
            feedback.save()
            messages.success(request, "Thank you for rating our resolution service!")
    return redirect("complaints:detail", ticket_number=ticket_number)

