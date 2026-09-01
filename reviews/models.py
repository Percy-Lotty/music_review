import requests
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Album(models.Model):
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    release_date = models.DateField()
    cover_url = models.URLField(blank=True)
    genre = models.CharField(max_length=100, blank=True)
    label = models.CharField(max_length=100, blank=True)

    # 乐评字段内联在 Album 上而非独立建表：一张专辑最多一份乐评，独立成表只会多一次连表
    critic_score = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    critic_review = models.TextField(blank=True)
    critic_name = models.CharField(max_length=100, blank=True)
    critic_published_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.artist}"

    def fetch_cover_from_itunes(self):
        """抓取并保存专辑封面，成功返回封面 URL，失败返回 None。

        使用 iTunes Search API，无需申请密钥。
        """
        url = "https://itunes.apple.com/search"
        params = {
            "term": f"{self.artist} {self.title}",
            "media": "music",
            "entity": "album",
            "limit": 1,
        }

        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            if data["resultCount"] > 0:
                # iTunes 把图片尺寸写在文件名里，替换后即可取到未公开的 1000x1000 高清图
                cover_url = data["results"][0]["artworkUrl100"].replace(
                    "100x100", "1000x1000"
                )
                self.cover_url = cover_url
                self.save()
                return cover_url
        except (requests.RequestException, KeyError, IndexError) as e:
            # 封面是附加信息，网络或返回格式异常不应连带专辑本身一起保存失败。
            # 只捕获这三类：其他异常（如拼写错误引发的 AttributeError）应当暴露出来
            print(f"iTunes 获取封面失败：{e}")

        return None


class UserRating(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="ratings")
    score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    reviewer_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        name = self.reviewer_name or "匿名用户"
        return f"{name} - {self.album.title} - {self.score}分"
