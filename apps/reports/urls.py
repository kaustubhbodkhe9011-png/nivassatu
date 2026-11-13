from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.reports_overview_view, name="overview"),
    path("export/complaints/", views.export_complaints_csv, name="export_complaints"),
    path("export/dues/", views.export_dues_csv, name="export_dues"),
]
