from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.landing_page, name="landing"),
    path("dashboard/", views.dashboard_dispatcher, name="dashboard"),
    path("dashboard/secretary/", views.secretary_dashboard, name="secretary_dashboard"),
    path("dashboard/resident/", views.resident_dashboard, name="resident_dashboard"),
    path("dashboard/staff/", views.staff_dashboard, name="staff_dashboard"),
]

