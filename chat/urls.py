from django.urls import path
from . import views

urlpatterns: list[str] = [
    path("<str:room_id>/", views.fetch_room_messages),
    path("read/<str:room_id>/", views.update_read_status),
]
