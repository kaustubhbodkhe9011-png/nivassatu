from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.core.decorators import secretary_required
from .models import Notice, NoticeAcknowledgement
from .forms import NoticeForm

@login_required
def notice_list_view(request):
    """Notice board listing pinned and recent notices."""
    notices = Notice.objects.select_related("published_by").prefetch_related("acknowledgements").all()
    user_ack_ids = set(NoticeAcknowledgement.objects.filter(user=request.user).values_list("notice_id", flat=True))

    return render(request, "notices/notice_list.html", {
        "notices": notices,
        "user_ack_ids": user_ack_ids,
    })

@login_required
@secretary_required
def create_notice_view(request):
    """Secretary action: publish new notice."""
    if request.method == "POST":
        form = NoticeForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.published_by = request.user
            notice.save()
            messages.success(request, f"Notice '{notice.title}' published successfully.")
            return redirect("notices:list")
    else:
        form = NoticeForm()
    return render(request, "notices/create_notice.html", {"form": form})

@login_required
def acknowledge_notice_view(request, notice_id):
    """Resident action: mark notice as read/acknowledged."""
    notice = get_object_or_404(Notice, id=notice_id)
    NoticeAcknowledgement.objects.get_or_create(notice=notice, user=request.user)
    messages.success(request, f"Acknowledged notice: {notice.title}")
    return redirect("notices:list")

