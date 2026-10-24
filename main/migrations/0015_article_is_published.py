from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0014_follow"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="is_published",
            field=models.BooleanField(default=True),
        ),
    ]
