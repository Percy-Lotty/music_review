from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, render

from .models import Album


def home(request):
    query = request.GET.get("q", "").strip()
    albums = Album.objects.all()

    if query:
        # 用 Q 组合成 OR；写成两个关键字参数会变成 AND，等于要求标题和艺人同时命中
        albums = albums.filter(Q(title__icontains=query) | Q(artist__icontains=query))

    return render(request, "reviews/home.html", {"albums": albums, "query": query})


def album_detail(request, album_id):
    album = get_object_or_404(Album, id=album_id)

    user_ratings = album.ratings.all()
    avg_score = user_ratings.aggregate(Avg("score"))["score__avg"]

    # 一条评分都没有时 aggregate 返回 None，不能直接丢给 round
    if avg_score is not None:
        avg_score = round(avg_score, 1)

    return render(
        request,
        "reviews/album_detail.html",
        {"album": album, "avg_score": avg_score},
    )


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
