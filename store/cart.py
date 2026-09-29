from .models import Cart


def get_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    cart, _ = Cart.objects.get_or_create(session_key=session_key, user=None)
    return cart


def merge_session_cart_into_user(request, user):
    # runs on login/register so the guest cart isn't lost
    if not request.session.session_key:
        return
    session_cart = Cart.objects.filter(session_key=request.session.session_key, user__isnull=True).first()
    if not session_cart:
        return
    user_cart, _ = Cart.objects.get_or_create(user=user)
    user_cart.merge_from(session_cart)
