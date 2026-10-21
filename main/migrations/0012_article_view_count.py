
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0011_article_view_count"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name="article",
                    name="view_count",
                    field=__import__(
                        "django.db.models",
                        fromlist=["PositiveIntegerField"],
                    ).PositiveIntegerField(default=0),
                ),
            ],
        ),
    ]
