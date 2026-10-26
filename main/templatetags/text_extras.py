import html

from django import template
from django.utils.html import strip_tags

register = template.Library()


@register.filter
def plain_text(value):
    text = strip_tags(value or "")
    text = html.unescape(text)
    return text.replace("\xa0", " ")
