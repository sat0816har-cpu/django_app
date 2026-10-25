from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0016_comment_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="user_was_registered",
            field=models.BooleanField(default=False),
        ),
    ]
