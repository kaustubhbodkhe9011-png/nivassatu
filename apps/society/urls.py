from django.urls import path
from . import views

app_name = "society"

urlpatterns = [
    path("flats/", views.flat_list_view, name="flats"),
    path("flats/add/", views.add_flat_view, name="add_flat"),
    path("residents/", views.resident_list_view, name="residents"),
    path("residents/assign/", views.assign_resident_view, name="assign_resident"),
]
