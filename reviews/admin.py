from django.contrib import admin
from django.utils.html import format_html

from .models import Album, UserRating

# 站点品牌信息：admin 自带模板会读取这三个属性，改属性即可生效，无需动模板
admin.site.site_header = "乐评项目管理后台"
admin.site.site_title = "乐评后台"  # 浏览器标签页标题
admin.site.index_title = "欢迎使用乐评后台"  # 后台首页大标题


class UserRatingInline(admin.TabularInline):
    model = UserRating
    extra = 1
    classes = ["collapse"]  # 默认折叠，点开才显示，和 fieldsets 的 collapse 用法一致
    verbose_name = "用户评分"
    verbose_name_plural = (
        "用户评分"  # 内联标题用的是复数名，两个都设成中文避免被加上英文 s
    )


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

    fieldsets = [
        (
            "专辑信息",
            {
                "fields": [
                    "title",
                    "artist",
                    "release_date",
                    "cover_url",
                    "genre",
                    "label",
                ]
            },
        ),
        (
            "乐评",
            {
                "fields": [
                    "critic_score",
                    "critic_review",
                    "critic_name",
                    "critic_published_at",
                ],
                "classes": ["collapse"],
            },
        ),  # collapse = 默认折叠，点开才显示
    ]

    inlines = [UserRatingInline]

    def cover_preview(self, obj):
        """列表页的封面缩略图列。"""
        if obj.cover_url:
            # format_html：模板部分信任，参数自动转义；此处 URL 来自 iTunes API 而非用户输入
            return format_html(
                '<img src = "{}" width = "50" height = "50" style = "object-fit: cover;" />',
                obj.cover_url,
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
