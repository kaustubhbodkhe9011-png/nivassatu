from django.urls import path
from . import views

app_name = "notices"

urlpatterns = [
    path("", views.notice_list_view, name="list"),
    path("new/", views.create_notice_view, name="create"),
    path("<int:notice_id>/ack/", views.acknowledge_notice_view, name="acknowledge"),
]
