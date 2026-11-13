from django.urls import path
from . import views

app_name = "complaints"

urlpatterns = [
    path("", views.complaint_list_view, name="list"),
    path("new/", views.create_complaint_view, name="create"),
    path("<str:ticket_number>/", views.complaint_detail_view, name="detail"),
    path("<str:ticket_number>/assign/", views.assign_staff_view, name="assign"),
    path("<str:ticket_number>/status/", views.update_status_view, name="update_status"),
    path("<str:ticket_number>/comment/", views.add_comment_view, name="add_comment"),
    path("<str:ticket_number>/feedback/", views.submit_feedback_view, name="feedback"),
]
