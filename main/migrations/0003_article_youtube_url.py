
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0002_article_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="youtube_url",
            field=models.URLField(
                blank=True,
                default=""
            ),
        ),
    ]
