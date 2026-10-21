
from django.db import migrations


def repair_articleview_table(apps, schema_editor):
    ArticleView = apps.get_model("main", "ArticleView")
    table_name = ArticleView._meta.db_table

    with schema_editor.connection.cursor() as cursor:
        tables = schema_editor.connection.introspection.table_names(
            cursor
        )

    if table_name in tables:
        schema_editor.execute(
            f"DROP TABLE {schema_editor.quote_name(table_name)}"
        )

    schema_editor.create_model(ArticleView)


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0012_article_view_count"),
    ]

    operations = [
        migrations.RunPython(
            repair_articleview_table,
            migrations.RunPython.noop,
        ),
    ]
