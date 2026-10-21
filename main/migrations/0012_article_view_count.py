
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ("main", "0011_article_view_count"),
]

    operations = [
        migrations.AddField(
            model_name="article",
            name="view_count",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
