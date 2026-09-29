from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from .cart import get_cart, merge_session_cart_into_user
from .forms import (
    AddToCartForm, CheckoutForm, LoginForm, NewsletterForm, ProfileForm, RegisterForm, ReviewForm,
)
from .models import Category, Order, OrderItem, Product


# ---------------------------------------------------------------- helpers --

def _safe_int(value, default=None):
    # so a bad quantity in POST doesn't 500 the page
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# ------------------------------------------------------------------ pages --

def home(request):
    categories = Category.objects.all()
    featured = Product.with_ratings().filter(is_featured=True)[:8]
    deals = Product.with_ratings().filter(is_deal_of_the_day=True)[:4]
    stats = {
        "categories": Category.objects.count(),
        "products": Product.objects.count(),
        "customers": 1200,
    }
    return render(request, "store/home.html", {
        "categories": categories,
        "featured": featured,
        "deals": deals,
        "newsletter_form": NewsletterForm(),
        "stats": stats,
    })


@require_POST
def newsletter_signup(request):
    form = NewsletterForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "Thanks for subscribing — check your inbox for plant tips soon!")
    else:
        messages.error(request, "Please enter a valid email address.")
    return redirect(request.META.get("HTTP_REFERER", "store:home"))


def product_list(request):
    products = Product.with_ratings().select_related("category")

    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    category_slug = request.GET.get("category", "").strip()
    active_category = None
    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=active_category)

    sort = request.GET.get("sort", "")
    sort_map = {
        "price_asc": "price",
        "price_desc": "-price",
        "rating": "-avg_rating",
        "newest": "-created_at",
    }
    products = products.order_by(sort_map.get(sort, "-created_at"))

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "store/product_list.html", {
        "page_obj": page_obj,
        "categories": Category.objects.all(),
        "active_category": active_category,
        "query": query,
        "sort": sort,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product.with_ratings().select_related("category"), slug=slug)
    reviews = product.reviews.select_related("user").all()
    related = Product.objects.filter(category=product.category).exclude(pk=product.pk)[:4]

    user_has_reviewed = (
        request.user.is_authenticated and reviews.filter(user=request.user).exists()
    )
    review_form = ReviewForm() if request.user.is_authenticated and not user_has_reviewed else None

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to leave a review.")
            return redirect("store:login")
        if user_has_reviewed:
            messages.error(request, "You've already reviewed this product.")
            return redirect(product.get_absolute_url())
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Thanks — your review has been posted.")
            return redirect(product.get_absolute_url())

    return render(request, "store/product_detail.html", {
        "product": product,
        "reviews": reviews,
        "related": related,
        "review_form": review_form,
        "user_has_reviewed": user_has_reviewed,
        "add_form": AddToCartForm(),
    })


# ------------------------------------------------------------------- cart --

def cart_detail(request):
    cart = get_cart(request)
    return render(request, "store/cart.html", {"cart": cart})


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    qty = _safe_int(request.POST.get("quantity"), default=None)
    if qty is None or qty < 1:
        messages.error(request, "Please enter a valid quantity.")
        return redirect(request.META.get("HTTP_REFERER", product.get_absolute_url()))

    cart = get_cart(request)
    existing = cart.items.filter(product=product).first()
    current_qty = existing.quantity if existing else 0
    requested_total = current_qty + qty

    if requested_total > product.stock:
        if current_qty:
            messages.error(
                request,
                f'Only {product.stock} of "{product.name}" left in stock '
                f'(you already have {current_qty} in your cart).',
            )
        else:
            messages.error(request, f'Only {product.stock} of "{product.name}" left in stock.')
        return redirect(request.META.get("HTTP_REFERER", product.get_absolute_url()))

    if existing:
        existing.quantity = requested_total
        existing.save()
    else:
        cart.items.create(product=product, quantity=qty)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "cart_item_count": cart.total_items})

    messages.success(request, f'Added "{product.name}" to your cart.')
    return redirect(request.META.get("HTTP_REFERER", product.get_absolute_url()))


@require_POST
def cart_update(request, item_id):
    cart = get_cart(request)
    item = get_object_or_404(cart.items, pk=item_id)
    qty = _safe_int(request.POST.get("quantity"), default=None)

    if qty is None or qty < 1:
        messages.error(request, "Quantity must be a positive whole number.")
        return redirect("store:cart_detail")

    if qty > item.product.stock:
        messages.error(request, f'Only {item.product.stock} of "{item.product.name}" available.')
        return redirect("store:cart_detail")

    item.quantity = qty
    item.save()
    messages.success(request, "Cart updated.")
    return redirect("store:cart_detail")


@require_POST
def cart_remove(request, item_id):
    cart = get_cart(request)
    item = get_object_or_404(cart.items, pk=item_id)
    item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect("store:cart_detail")


# --------------------------------------------------------------- checkout --

@login_required
@never_cache
def checkout(request):
    cart = get_cart(request)
    items = list(cart.items.select_related("product"))

    if not items:
        messages.info(request, "Your cart is empty.")
        return redirect("store:product_list")

    profile = getattr(request.user, "profile", None)
    initial = {"full_name": request.user.get_full_name() or request.user.username}
    if profile:
        initial.update({
            "phone": profile.phone,
            "address_line1": profile.address_line1,
            "address_line2": profile.address_line2,
            "city": profile.city,
            "state": profile.state,
            "postal_code": profile.postal_code,
            "country": profile.country,
        })

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = None
            try:
                with transaction.atomic():
                    # lock these rows so two checkouts can't both grab the last item
                    product_ids = [i.product_id for i in items]
                    locked_products = {
                        p.pk: p for p in Product.objects.select_for_update().filter(pk__in=product_ids)
                    }

                    for item in items:
                        product = locked_products[item.product_id]
                        if item.quantity > product.stock:
                            raise ValueError(
                                f'"{product.name}" only has {product.stock} left in stock — '
                                f'please update your cart.'
                            )

                    subtotal = sum(locked_products[i.product_id].price * i.quantity for i in items)

                    order = Order.objects.create(
                        user=request.user,
                        subtotal=subtotal,
                        **form.cleaned_data,
                    )
                    for item in items:
                        product = locked_products[item.product_id]
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            product_name=product.name,
                            unit_price=product.price,
                            quantity=item.quantity,
                        )
                        product.stock = F("stock") - item.quantity  # subtract in the db, not in python
                        product.save(update_fields=["stock"])

                    cart.items.all().delete()
            except ValueError as exc:
                messages.error(request, str(exc))
                return redirect("store:cart_detail")

            messages.success(request, "Your order has been placed! (test mode — no real payment was taken)")
            return redirect("store:order_confirmation", order_id=order.pk)
    else:
        form = CheckoutForm(initial=initial)

    return render(request, "store/checkout.html", {"form": form, "cart": cart, "items": items})


@login_required
@never_cache
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, "store/order_confirmation.html", {"order": order})


@login_required
@never_cache
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    paginator = Paginator(orders, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "store/order_history.html", {"page_obj": page_obj})


@login_required
@never_cache
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, "store/order_detail.html", {"order": order})


# ---------------------------------------------------------------- account --

@method_decorator(never_cache, name="dispatch")
class PlantStoreLoginView(LoginView):
    # no-cache so back button doesn't show a logged-in page after someone logs out
    template_name = "store/login.html"
    form_class = LoginForm

    def form_valid(self, form):
        response = super().form_valid(form)
        merge_session_cart_into_user(self.request, self.request.user)
        return response

    def get(self, request, *args, **kwargs):
        # already logged in? don't show them a login form
        if request.user.is_authenticated:
            return redirect(self.get_success_url() if request.GET.get(self.redirect_field_name) else "store:home")
        return super().get(request, *args, **kwargs)


@method_decorator(never_cache, name="dispatch")
class PlantStoreLogoutView(LogoutView):
    next_page = "store:home"


def register(request):
    if request.user.is_authenticated:
        return redirect("store:home")

    next_url = request.POST.get("next") or request.GET.get("next")
    safe_next = next_url if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ) else None

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.first_name = form.cleaned_data["first_name"]
            user.save()
            auth_login(request, user)
            merge_session_cart_into_user(request, user)
            messages.success(request, f"Welcome to Verdant, {user.first_name}!")
            return redirect(safe_next or "store:home")
    else:
        form = RegisterForm()
    return render(request, "store/register.html", {"form": form, "next": safe_next})


@login_required
@never_cache
def profile(request):
    profile_obj = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile_obj)
        if form.is_valid():
            form.save()
            request.user.first_name = request.POST.get("first_name", request.user.first_name)
            request.user.last_name = request.POST.get("last_name", request.user.last_name)
            request.user.save()
            messages.success(request, "Profile updated.")
            return redirect("store:profile")
    else:
        form = ProfileForm(instance=profile_obj, initial={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
        })
    recent_orders = Order.objects.filter(user=request.user)[:5]
    return render(request, "store/profile.html", {
        "form": form, "recent_orders": recent_orders,
    })
