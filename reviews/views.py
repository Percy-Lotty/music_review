from django.db.models import Avg, Q
from django.shortcuts import render
from django.views import generic

from .models import Album


class AlbumListView(generic.ListView):
    model = Album
    template_name = "reviews/home.html"
    context_object_name = "albums"
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        if query:
            albums = Album.objects.filter(
                Q(title__icontains=query) | Q(artist__icontains=query)
            )
        else:
            albums = Album.objects.all()
        return albums.order_by("-release_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        return context


class AlbumDetailView(generic.DetailView):
    model = Album
    template_name = "reviews/album_detail.html"
    pk_url_kwarg = "album_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        avg_score = self.object.ratings.all().aggregate(Avg("score"))["score__avg"]
        context["avg_score"] = round(avg_score, 1) if avg_score is not None else None
        return context


def artist_albums(request, artist_name):
    albums = Album.objects.filter(artist__iexact=artist_name)

    return render(
        request,
        "reviews/artist_albums.html",
        {"albums": albums, "artist_name": artist_name},
    )


def critic_albums(request, critic_name):
    # critic_name 为空只代表"这张专辑没有乐评"，并非某位乐评人，必须排除以免被聚成一组
    albums = Album.objects.filter(critic_name__iexact=critic_name).exclude(
        critic_name=""
    )

    return render(
        request,
        "reviews/critic_albums.html",
        {"albums": albums, "critic_name": critic_name},
    )
