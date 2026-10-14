
from django.contrib.auth.models import User
from django.db import models


class Article(models.Model):
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

    image = models.ImageField(
        upload_to="articles/",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title
