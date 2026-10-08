from django.contrib.auth.models import User
from django.db import models


class Article(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
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
