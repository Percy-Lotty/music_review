from django.urls import path

from . import views

app_name = "reviews"
urlpatterns = [
    path("", views.AlbumListView.as_view(), name="home"),
    path("album/<int:album_id>/", views.AlbumDetailView.as_view(), name="album_detail"),
    path("album/<int:album_id>/rate/", views.add_rating, name="add_rating"),
    path("artist/<str:artist_name>/", views.artist_albums, name="artist_albums"),
    path("critic/<str:critic_name>/", views.critic_albums, name="critic_albums"),
]
