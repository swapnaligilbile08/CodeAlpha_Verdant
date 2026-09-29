from django import template

register = template.Library()


@register.filter
def star_display(rating):
    try:
        rating = float(rating)
    except (TypeError, ValueError):
        rating = 0
    full = int(round(rating))
    full = max(0, min(5, full))
    return "★" * full + "☆" * (5 - full)


@register.filter
def currency(value):
    try:
        return f"₹{float(value):,.2f}"
    except (TypeError, ValueError):
        return value
