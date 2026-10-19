
from django.contrib.auth.models import User
from django.db import models


class Article(models.Model):
    GENRE_CHOICES = [
        ("hobby", "趣味・エンタメ"),
        ("people", "人・社会"),
        ("life", "暮らし"),
        ("learning", "学び・仕事"),
        ("creative", "創作・表現"),
        ("other", "その他"),
    ]

    CATEGORY_CHOICES = [
        ("music", "音楽"),
        ("movie", "映画"),
        ("book", "読書"),
        ("photo", "写真"),
        ("travel", "旅行"),
        ("cooking", "料理"),
        ("other", "その他"),
    ]

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=200)
    content = models.TextField()

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="other"
    )

    genre = models.CharField(
        max_length=20,
        choices=GENRE_CHOICES,
        default="other"
    )

    sub_category = models.CharField(
        max_length=50,
        blank=True,
        default=""
    )

    image = models.ImageField(
        upload_to="articles/",
        blank=True,
        null=True
    )

    youtube_url = models.URLField(
        blank=True,
        default=""
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    like_count = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        return self.title


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    introduction = models.TextField(
        blank=True,
        default=""
    )

    favorite_things = models.CharField(
        max_length=300,
        blank=True,
        default=""
    )

    def __str__(self):
        return f"{self.user.username}のプロフィール"



class Comment(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    name = models.CharField(
        max_length=50
    )

    content = models.TextField(
        max_length=1000
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_approved = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.name} - {self.article.title}"

    class Meta:
        ordering = ["created_at"]


class ArticleImage(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="extra_images"
    )

    image = models.ImageField(
        upload_to="articles/"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.article.title}の追加画像"


class ArticleVideo(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="extra_videos"
    )

    youtube_url = models.URLField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.article.title}の追加動画"



