from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import generic

from .forms import RatingForm
from .models import Album, UserRating


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
        ratings = self.object.ratings.all()
        avg_score = ratings.aggregate(Avg("score"))["score__avg"]
        context["ratings"] = ratings
        context["avg_score"] = round(avg_score, 1) if avg_score is not None else None
        if self.request.user.is_authenticated:
            context["my_rating"] = self.object.ratings.filter(
                user=self.request.user
            ).first()
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


class RegisterView(generic.CreateView):
    form_class = UserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")


@login_required
def add_rating(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    # 已评过就把旧评分绑给表单：再次提交变成修改，而不是触发唯一约束 500
    existing = UserRating.objects.filter(album=album, user=request.user).first()

    if request.method == "POST":
        form = RatingForm(request.POST, instance=existing)
        if form.is_valid():
            rating = form.save(commit=False)  # 先不入库
            rating.album = album  # 补上表单里没有的字段
            rating.user = request.user
            rating.save()
            return redirect("reviews:album_detail", album_id=album.id)  # PRG！
    else:
        form = RatingForm(instance=existing)

    return render(request, "reviews/add_rating.html", {"form": form, "album": album})


class MyRatingsView(LoginRequiredMixin, generic.ListView):
    model = UserRating
    template_name = "reviews/my_ratings.html"
    context_object_name = "ratings"

    def get_queryset(self):
        return self.request.user.ratings.order_by("-created_at")
