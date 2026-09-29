from .cart import get_cart


def cart_summary(request):
    try:
        cart = get_cart(request)
        count = cart.total_items
    except Exception:
        count = 0
    return {"cart_item_count": count}
