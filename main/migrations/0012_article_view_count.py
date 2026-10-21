
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0011_articleview"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="view_count",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
