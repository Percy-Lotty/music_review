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
