from django import template

register = template.Library()

@register.filter(name='intspace')
def intspace(value):
    try:
        return f"{int(value):,}".replace(",", " ")
    except (ValueError, TypeError):
        return value