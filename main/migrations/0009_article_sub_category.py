
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0008_articleimage_articlevideo"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="sub_category",
            field=models.CharField(
                blank=True,
                default="",
                max_length=50,
            ),
        ),
    ]
