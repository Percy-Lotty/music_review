from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Album, UserRating


class AlbumModelTests(TestCase):
    def test_str_method(self):
        """__str__ 返回 '标题 - 艺人' 格式"""
        album = Album.objects.create(
            title="Silksong", artist="Team Cherry", release_date="2025-09-04"
        )
        self.assertEqual(str(album), "Silksong - Team Cherry")


class HomeViewTests(TestCase):
    def setUp(self):
        Album.objects.create(
            title="Silksong", artist="Team Cherry", release_date="2025-09-04"
        )
        Album.objects.create(
            title="Celeste", artist="EXOK Games", release_date="2018-01-25"
        )

    def test_home_page_return_200(self):
        """首页返回状态码 200"""
        response = self.client.get(reverse("reviews:home"))
        self.assertEqual(response.status_code, 200)

    def test_search_filters_by_artist(self):
        """搜索按艺人过滤"""
        response = self.client.get(reverse("reviews:home"), {"q": "EXOK Games"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["albums"]), 1)
        self.assertContains(response, "Celeste")
        self.assertNotContains(response, "Silksong")

    def test_search_ignore_case(self):
        """搜索忽略大小写"""
        response = self.client.get(reverse("reviews:home"), {"q": "exok games"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["albums"]), 1)
        self.assertContains(response, "Celeste")


class AlbumDetailViewTests(TestCase):
    def setUp(self):
        Album.objects.create(
            title="Silksong", artist="Team Cherry", release_date="2025-09-04"
        )
        UserRating.objects.create(
            album=Album.objects.get(title="Silksong"), score=9, reviewer_name="Ori"
        )
        UserRating.objects.create(
            album=Album.objects.get(title="Silksong"), score=8, reviewer_name="Issac"
        )
        UserRating.objects.create(
            album=Album.objects.get(title="Silksong"), score=10, reviewer_name="Hornet"
        )

    def test_nonexistent_album(self):
        """不存在的专辑返回 404"""
        response = self.client.get(
            reverse("reviews:album_detail", kwargs={"album_id": 1000000})
        )
        self.assertEqual(response.status_code, 404)

    def test_avg_score_is_correct(self):
        """平均评分正确"""
        response = self.client.get(
            reverse(
                "reviews:album_detail",
                kwargs={"album_id": Album.objects.get(title="Silksong").id},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["avg_score"], 9.0)

    def test_rating_list_shown(self):
        """评分列表显示"""
        response = self.client.get(
            reverse(
                "reviews:album_detail",
                kwargs={"album_id": Album.objects.get(title="Silksong").id},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["ratings"]), 3)
        self.assertContains(response, "Ori")
        self.assertContains(response, "共3条评分")


class CriticViewTests(TestCase):
    def setUp(self):
        Album.objects.create(
            title="Silksong",
            artist="Team Cherry",
            release_date="2025-09-04",
            critic_name="Ori",
        )
        Album.objects.create(
            title="Celeste",
            artist="EXOK Games",
            release_date="2018-01-25",
            critic_name="Ori",
        )
        Album.objects.create(
            title="Hollow Knight",
            artist="Team Cherry",
            release_date="2017-02-25",
            critic_name="Issac",
        )
        Album.objects.create(
            title="Cuphead",
            artist="Studio MDHR",
            release_date="2017-09-29",
            critic_name="",
        )

    def test_critic_page_filters_by_name(self):
        """乐评人过滤"""
        response = self.client.get(
            reverse("reviews:critic_albums", kwargs={"critic_name": "Ori"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["albums"]), 2)
        self.assertContains(response, "Silksong")
        self.assertNotContains(response, "Hollow Knight")
        self.assertNotContains(response, "Cuphead")


class PaginationTests(TestCase):
    def setUp(self):
        for i in range(13):
            Album.objects.create(
                title=f"Album {i}", artist="Tester", release_date="2024-01-01"
            )

    def test_home_paginates_by_12(self):
        """超过 12 张时首页分页，第二页剩 1 张"""
        response = self.client.get(reverse("reviews:home"))
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["albums"]), 12)

        page2 = self.client.get(reverse("reviews:home"), {"page": 2})
        self.assertEqual(len(page2.context["albums"]), 1)


class RatingViewTests(TestCase):
    """评分提交：登录拦截、成功提交、重复评分处理"""

    def setUp(self):
        self.album = Album.objects.create(
            title="Silksong", artist="Team Cherry", release_date="2025-09-04"
        )
        self.user = User.objects.create_user(username="percy", password="pass12345")
        self.url = reverse("reviews:add_rating", kwargs={"album_id": self.album.id})

    def test_anonymous_redirected_to_login(self):
        """未登录访问评分页跳转登录页，并带上回跳地址"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
        self.assertIn("next=", response.url)

    def test_detail_page_shows_entry_to_anonymous(self):
        """未登录时详情页也有「我要评分」入口，指向评分页"""
        detail = self.client.get(
            reverse("reviews:album_detail", kwargs={"album_id": self.album.id})
        )
        self.assertContains(detail, "我要评分")
        self.assertContains(
            detail, reverse("reviews:add_rating", kwargs={"album_id": self.album.id})
        )

    def test_login_redirect_round_trip(self):
        """未登录点进评分页 → 登录 → 回到评分页（完整往返）"""
        first = self.client.get(self.url)
        self.assertEqual(first.status_code, 302)
        self.assertIn("/accounts/login/", first.url)

        login_resp = self.client.post(
            first.url, {"username": "percy", "password": "pass12345"}
        )
        self.assertRedirects(login_resp, self.url)

    def test_logged_in_user_can_submit_rating(self):
        """登录后提交评分成功，分数进入详情页与平均分"""
        self.client.force_login(self.user)
        response = self.client.post(self.url, {"score": 8})
        self.assertRedirects(
            response,
            reverse("reviews:album_detail", kwargs={"album_id": self.album.id}),
        )

        rating = UserRating.objects.get()
        self.assertEqual(rating.user, self.user)
        self.assertEqual(rating.score, 8)

        detail = self.client.get(
            reverse("reviews:album_detail", kwargs={"album_id": self.album.id})
        )
        self.assertContains(detail, "percy")
        self.assertEqual(detail.context["avg_score"], 8.0)

    def test_duplicate_rating_not_created_twice(self):
        """同一账号重复评分：不新增第二行，改为更新原分数"""
        self.client.force_login(self.user)
        self.client.post(self.url, {"score": 8})
        response = self.client.post(self.url, {"score": 6})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(UserRating.objects.count(), 1)
        self.assertEqual(UserRating.objects.get().score, 6)

    def test_out_of_range_score_rejected(self):
        """超出 0-10 的分数被表单拦下，不落库"""
        self.client.force_login(self.user)
        response = self.client.post(self.url, {"score": 11})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserRating.objects.count(), 0)


class MyRatingsViewTests(TestCase):
    """个人中心：登录保护与只展示自己的评分"""

    def setUp(self):
        self.my_album = Album.objects.create(
            title="Celeste", artist="EXOK Games", release_date="2018-01-25"
        )
        self.other_album = Album.objects.create(
            title="Cuphead", artist="Studio MDHR", release_date="2017-09-29"
        )
        self.user = User.objects.create_user(username="percy", password="pass12345")
        self.other_user = User.objects.create_user(
            username="someone", password="pass12345"
        )
        UserRating.objects.create(album=self.my_album, user=self.user, score=9)
        UserRating.objects.create(album=self.other_album, user=self.other_user, score=3)

    def test_my_ratings_requires_login(self):
        """未登录访问个人中心跳转登录页"""
        response = self.client.get(reverse("reviews:my_ratings"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_my_ratings_shows_only_own(self):
        """登录后只看到自己的评分"""
        self.client.force_login(self.user)
        response = self.client.get(reverse("reviews:my_ratings"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["ratings"]), 1)
        self.assertContains(response, "Celeste")
        self.assertNotContains(response, "Cuphead")


class RegisterViewTests(TestCase):
    """注册页：成功注册并登录、密码不一致不建号"""

    def test_register_success_then_login(self):
        """注册成功跳登录页，新账号能登录"""
        response = self.client.post(
            reverse("reviews:register"),
            {
                "username": "newbie",
                "password1": "Zq3-very-secret",
                "password2": "Zq3-very-secret",
            },
        )
        self.assertRedirects(response, reverse("login"))
        self.assertTrue(User.objects.filter(username="newbie").exists())
        self.assertTrue(
            self.client.login(username="newbie", password="Zq3-very-secret")
        )

    def test_register_password_mismatch_creates_no_user(self):
        """两次密码不一致时重新渲染注册页，不创建用户"""
        response = self.client.post(
            reverse("reviews:register"),
            {
                "username": "oops",
                "password1": "Zq3-very-secret",
                "password2": "different-pass",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="oops").exists())
