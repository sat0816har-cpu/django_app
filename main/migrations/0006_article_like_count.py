
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0005_profile"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="like_count",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
