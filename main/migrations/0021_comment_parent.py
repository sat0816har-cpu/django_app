
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_profile_is_withdrawn'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='parent',
            field=models.ForeignKey(
                to='main.comment',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='replies',
                null=True,
                blank=True,
            ),
        ),
    ]
