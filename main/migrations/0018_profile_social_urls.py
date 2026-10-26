from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0017_comment_user_was_registered"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="website_url",
            field=models.URLField(
                blank=True,
                default="",
                max_length=500,
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="x_url",
            field=models.URLField(
                blank=True,
                default="",
                max_length=500,
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="instagram_url",
            field=models.URLField(
                blank=True,
                default="",
                max_length=500,
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="youtube_url",
            field=models.URLField(
                blank=True,
                default="",
                max_length=500,
            ),
        ),
    ]
