from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("album/<int:album_id>/", views.album_detail, name="album_detail"),
    path("artist/<str:artist_name>/", views.artist_albums, name="artist_albums"),
    path("critic/<str:critic_name>/", views.critic_albums, name="critic_albums"),
]
