from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Album, UserRating


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "artist",
        "release_date",
        "critic_score",
        "critic_name",
        "critic_published_at",
        "genre",
        "label",
        "cover_preview",
    )
    fields = (
        "title",
        "artist",
        "release_date",
        "cover_url",
        "genre",
        "label",
        "critic_score",
        "critic_review",
        "critic_name",
        "critic_published_at",
    )

    def cover_preview(self, obj):
        """列表页的封面缩略图列。"""
        if obj.cover_url:
            # mark_safe 会跳过转义，此处拼接的是 iTunes 返回的 URL 而非用户输入
            return mark_safe(
                f'<img src="{obj.cover_url}" width="50" height="50" '
                'style="object-fit: cover;" />'
            )
        return "无封面"

    cover_preview.short_description = "封面"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # 后台录入时通常只填标题和艺人，这里顺手补一张封面，省去手动找图
        if not obj.cover_url and obj.title and obj.artist:
            cover_url = obj.fetch_cover_from_itunes()
            if cover_url:
                self.message_user(request, "成功获取封面图片！")


class ScoreRangeFilter(admin.SimpleListFilter):
    title = "评分范围"
    parameter_name = "score_range"

    def lookups(self, request, model_admin):
        return (
            ("low", "低分 (1-3分)"),
            ("medium", "中分 (4-7分)"),
            ("high", "高分 (8-10分)"),
        )

    def queryset(self, request, queryset):
        if self.value() == "low":
            return queryset.filter(score__range=(1, 3))
        elif self.value() == "medium":
            return queryset.filter(score__range=(4, 7))
        elif self.value() == "high":
            return queryset.filter(score__range=(8, 10))
        return queryset


@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    list_display = ("album", "score", "reviewer_name", "created_at")
    list_filter = ("album", ScoreRangeFilter)
    search_fields = ("reviewer_name", "album__title")
