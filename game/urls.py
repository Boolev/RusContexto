from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('room/<int:room_id>/', views.render_room, name='render_room'),
    path('room_registration/', views.room_registration, name='room_registration'),
    path('delete_all_rooms/', views.delete_all_rooms, name='delete_all_rooms'),
    path('info/<int:room_id>/', views.show_room_info, name='show_room_info'),
]
