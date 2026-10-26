
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

    is_published = models.BooleanField(
        default=True
    )


    like_count = models.PositiveIntegerField(
        default=0
    )

    view_count = models.PositiveIntegerField(
    default=0
    )

    def __str__(self):
        return self.title


class ArticleLike(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="likes"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.article.title}へのいいね"

    class Meta:
        ordering = ["-created_at"]



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

        website_url = models.URLField(
        max_length=500,
        blank=True,
        default=""
    )

    x_url = models.URLField(
        max_length=500,
        blank=True,
        default=""
    )

    instagram_url = models.URLField(
        max_length=500,
        blank=True,
        default=""
    )

    youtube_url = models.URLField(
        max_length=500,
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

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="comments"
    )

    user_was_registered = models.BooleanField(
        default=False
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


class ArticleView(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="views"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.article.title}の閲覧"
    
    class Meta:
        ordering = ["-created_at"]


class Follow(models.Model):
    # フォローするユーザー
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following"
    )

    # フォローされるユーザー
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        # 同じ相手を重複してフォローできないようにする
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"],
                name="unique_user_follow"
            )
        ]

    def __str__(self):
        return f"{self.follower.username} → {self.following.username}"





