
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0003_article_youtube_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="genre",
            field=models.CharField(
                choices=[
                    ("hobby", "趣味・エンタメ"),
                    ("people", "人・社会"),
                    ("life", "暮らし"),
                    ("learning", "学び・仕事"),
                    ("creative", "創作・表現"),
                    ("other", "その他"),
                ],
                default="other",
                max_length=20,
            ),
        ),
    ]
