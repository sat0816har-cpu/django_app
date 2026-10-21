
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0010_articlelike"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="view_count",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
