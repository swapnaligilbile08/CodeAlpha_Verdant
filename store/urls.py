from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

app_name = "store"

urlpatterns = [
    path("", views.home, name="home"),
    path("newsletter/", views.newsletter_signup, name="newsletter_signup"),

    path("products/", views.product_list, name="product_list"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),

    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:item_id>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:item_id>/", views.cart_remove, name="cart_remove"),

    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.order_history, name="order_history"),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
    path("orders/<int:order_id>/confirmation/", views.order_confirmation, name="order_confirmation"),

    path("account/login/", views.PlantStoreLoginView.as_view(), name="login"),
    path("account/logout/", views.PlantStoreLogoutView.as_view(), name="logout"),
    path("account/register/", views.register, name="register"),
    path("account/profile/", views.profile, name="profile"),

    path(
        "account/password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="store/password_reset.html",
            email_template_name="store/password_reset_email.txt",
            subject_template_name="store/password_reset_subject.txt",
            success_url=reverse_lazy("store:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "account/password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="store/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "account/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="store/password_reset_confirm.html",
            success_url=reverse_lazy("store:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "account/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="store/password_reset_complete.html"),
        name="password_reset_complete",
    ),
]
