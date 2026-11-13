from django.urls import path
from . import views

app_name = "dues"

urlpatterns = [
    path("", views.dues_list_view, name="list"),
    path("generate/", views.generate_dues_view, name="generate"),
    path("record/<int:dues_id>/", views.record_payment_view, name="record_payment"),
    path("receipt/<str:receipt_number>/", views.receipt_view, name="receipt"),
]
