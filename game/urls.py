from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('room/<int:room_id>/', views.render_room, name='render_room'),
    path('room_registration/', views.room_registration, name='room_registration'),
]
