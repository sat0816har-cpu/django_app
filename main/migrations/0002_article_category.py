
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="category",
            field=models.CharField(
                max_length=20,
                choices=[
                    ("music", "音楽"),
                    ("movie", "映画"),
                    ("book", "読書"),
                    ("photo", "写真"),
                    ("travel", "旅行"),
                    ("cooking", "料理"),
                    ("other", "その他"),
                ],
                default="other",
            ),
        ),
    ]
