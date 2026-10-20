
from .models import Article


def sidebar_sub_categories(request):
    sidebar_categories = []

    for slug, name in Article.CATEGORY_CHOICES:
        sub_categories = (
            Article.objects
            .filter(category=slug)
            .exclude(sub_category="")
            .values_list("sub_category", flat=True)
            .distinct()
            .order_by("sub_category")
        )

        sidebar_categories.append({
            "slug": slug,
            "name": name,
            "sub_categories": list(sub_categories),
        })

    return {
        "sidebar_categories": sidebar_categories,
    }
