from django import template
import re

register = template.Library()


@register.filter
def slugify(value):
    value = value.lower()
    value = re.sub(r'\s+', '-', value)
    return value
