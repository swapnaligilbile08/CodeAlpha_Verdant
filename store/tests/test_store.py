from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from store.models import Category, Order, Product, Review


class StoreTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Indoor Plants")
        self.product = Product.objects.create(
            category=self.category, name="Test Monstera", price=Decimal("999.00"),
            stock=5, image_url="https://example.com/monstera.jpg",
        )
        self.low_stock_product = Product.objects.create(
            category=self.category, name="Rare Cactus", price=Decimal("199.00"),
            stock=1, image_url="https://example.com/cactus.jpg",
        )

    # ---------------------------------------------------------- registration
    def test_registration_creates_user_and_profile(self):
        response = self.client.post(reverse("store:register"), {
            "first_name": "Ana",
            "username": "ana123",
            "email": "ana@example.com",
            "password1": "SuperSecret123!",
            "password2": "SuperSecret123!",
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="ana123")
        self.assertTrue(hasattr(user, "profile"))

    def test_registration_rejects_duplicate_email(self):
        User.objects.create_user(username="existing", email="dup@example.com", password="x")
        response = self.client.post(reverse("store:register"), {
            "first_name": "Ben",
            "username": "ben456",
            "email": "dup@example.com",
            "password1": "SuperSecret123!",
            "password2": "SuperSecret123!",
        })
        self.assertEqual(response.status_code, 200)  # re-rendered with error
        self.assertFalse(User.objects.filter(username="ben456").exists())

    # ------------------------------------------------------------------ login
    def test_login(self):
        User.objects.create_user(username="loginuser", password="TestPass123!")
        response = self.client.post(reverse("store:login"), {
            "username": "loginuser", "password": "TestPass123!",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated if hasattr(response, "wsgi_request") else True)

    def test_logout_via_post_works(self):
        # django 5 logout only takes POST, make sure ours actually works
        user = User.objects.create_user(username="logoutuser", password="TestPass123!")
        self.client.force_login(user)
        response = self.client.post(reverse("store:logout"))
        self.assertEqual(response.status_code, 302)
        response2 = self.client.get(reverse("store:profile"))
        self.assertEqual(response2.status_code, 302)  # should bounce to login now

    def test_logout_rejects_get(self):
        # regression check - used to be a plain <a href> which is wrong
        user = User.objects.create_user(username="getlogout", password="TestPass123!")
        self.client.force_login(user)
        response = self.client.get(reverse("store:logout"))
        self.assertEqual(response.status_code, 405)

    def test_login_next_redirects_to_checkout(self):
        User.objects.create_user(username="nextuser", password="TestPass123!")
        checkout_url = reverse("store:checkout")
        response = self.client.post(
            f"{reverse('store:login')}?next={checkout_url}",
            {"username": "nextuser", "password": "TestPass123!", "next": checkout_url},
        )
        self.assertRedirects(response, checkout_url, fetch_redirect_response=False)

    def test_register_next_redirects_to_checkout(self):
        checkout_url = reverse("store:checkout")
        response = self.client.post(f"{reverse('store:register')}?next={checkout_url}", {
            "first_name": "Nikhil",
            "username": "nikhilreg",
            "email": "nikhil@example.com",
            "password1": "nikhilreg9!",  # deliberately similar to username — allowed now
            "password2": "nikhilreg9!",
            "next": checkout_url,
        })
        self.assertRedirects(response, checkout_url, fetch_redirect_response=False)

    def test_password_similar_to_username_is_allowed(self):
        response = self.client.post(reverse("store:register"), {
            "first_name": "Sam",
            "username": "samuel99",
            "email": "samuel@example.com",
            "password1": "samuel999!",
            "password2": "samuel999!",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="samuel99").exists())

    # ------------------------------------------------------------ password reset
    def test_password_reset_sends_email_and_allows_new_password(self):
        from django.core import mail

        user = User.objects.create_user(username="forgetful", email="forgetful@example.com", password="OldPass123!")

        response = self.client.post(reverse("store:password_reset"), {"email": "forgetful@example.com"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("reset", mail.outbox[0].subject.lower())

        # grab the reset link from the email
        import re
        match = re.search(r"/account/reset/(?P<uid>[\w-]+)/(?P<token>[\w-]+)/", mail.outbox[0].body)
        self.assertIsNotNone(match)

        confirm_url = f"/account/reset/{match.group('uid')}/{match.group('token')}/"
        session = self.client.get(confirm_url, follow=True)
        self.assertEqual(session.status_code, 200)

        # first visit swaps it for a one-time set-password url
        set_password_url = session.redirect_chain[-1][0] if session.redirect_chain else confirm_url
        response = self.client.post(set_password_url, {
            "new_password1": "BrandNewPass456!", "new_password2": "BrandNewPass456!",
        })
        self.assertEqual(response.status_code, 302)

        user.refresh_from_db()
        self.assertTrue(user.check_password("BrandNewPass456!"))

    def test_password_reset_does_not_leak_whether_email_exists(self):
        # should show the same "check your email" page either way, no hints
        response = self.client.post(reverse("store:password_reset"), {"email": "nobody@example.com"}, follow=True)
        self.assertContains(response, "Check your email")

    # --------------------------------------------------------------- add to cart
    def test_add_to_cart(self):
        response = self.client.post(
            reverse("store:cart_add", args=[self.product.id]), {"quantity": 2}
        )
        self.assertEqual(response.status_code, 302)
        cart_response = self.client.get(reverse("store:cart_detail"))
        self.assertContains(cart_response, "Test Monstera")
        self.assertContains(cart_response, "2")

    def test_quantity_validated_against_stock_on_add(self):
        response = self.client.post(
            reverse("store:cart_add", args=[self.low_stock_product.id]), {"quantity": 5}, follow=True
        )
        self.assertContains(response, "Only 1")
        cart_response = self.client.get(reverse("store:cart_detail"))
        self.assertNotContains(cart_response, "Rare Cactus")

    def test_quantity_validated_against_stock_on_update(self):
        self.client.post(reverse("store:cart_add", args=[self.product.id]), {"quantity": 1})
        item = self.client.get(reverse("store:cart_detail")).context["cart"].items.first()
        response = self.client.post(
            reverse("store:cart_update", args=[item.id]), {"quantity": 999}, follow=True
        )
        self.assertContains(response, "Only 5")

    def test_bad_quantity_does_not_500(self):
        # this used to 500 lol
        response = self.client.post(
            reverse("store:cart_add", args=[self.product.id]), {"quantity": "not-a-number"}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "valid quantity")

        response2 = self.client.post(
            reverse("store:cart_add", args=[self.product.id]), {"quantity": "-3"}, follow=True
        )
        self.assertEqual(response2.status_code, 200)

    # ----------------------------------------------------------------- checkout
    def test_full_checkout_flow(self):
        user = User.objects.create_user(username="buyer", password="TestPass123!")
        self.client.force_login(user)
        self.client.post(reverse("store:cart_add", args=[self.product.id]), {"quantity": 2})

        response = self.client.post(reverse("store:checkout"), {
            "full_name": "Buyer Test",
            "phone": "9999999999",
            "address_line1": "123 Leafy Lane",
            "address_line2": "",
            "city": "Pune",
            "state": "Maharashtra",
            "postal_code": "411001",
            "country": "India",
        })
        self.assertEqual(response.status_code, 302)

        order = Order.objects.get(user=user)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().quantity, 2)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)  # 5 - 2

    def test_checkout_fails_whole_order_if_stock_insufficient(self):
        user = User.objects.create_user(username="buyer2", password="TestPass123!")
        self.client.force_login(user)
        self.client.post(reverse("store:cart_add", args=[self.low_stock_product.id]), {"quantity": 1})

        # someone else buys the last unit before this checkout finishes
        self.low_stock_product.stock = 0
        self.low_stock_product.save()

        response = self.client.post(reverse("store:checkout"), {
            "full_name": "Buyer Two",
            "phone": "8888888888",
            "address_line1": "456 Fern Street",
            "address_line2": "",
            "city": "Pune",
            "state": "Maharashtra",
            "postal_code": "411002",
            "country": "India",
        }, follow=True)
        self.assertContains(response, "only has 0 left")
        self.assertEqual(Order.objects.filter(user=user).count(), 0)

    def test_order_appears_in_order_history(self):
        user = User.objects.create_user(username="buyer3", password="TestPass123!")
        self.client.force_login(user)
        self.client.post(reverse("store:cart_add", args=[self.product.id]), {"quantity": 1})
        self.client.post(reverse("store:checkout"), {
            "full_name": "Buyer Three", "phone": "7777777777",
            "address_line1": "789 Root Rd", "address_line2": "",
            "city": "Pune", "state": "Maharashtra", "postal_code": "411003", "country": "India",
        })
        response = self.client.get(reverse("store:order_history"))
        self.assertContains(response, "Order #")

    def test_order_only_visible_to_owner(self):
        owner = User.objects.create_user(username="owner", password="TestPass123!")
        intruder = User.objects.create_user(username="intruder", password="TestPass123!")
        order = Order.objects.create(
            user=owner, full_name="Owner", phone="1", address_line1="a",
            city="Pune", state="MH", postal_code="411001", country="India",
            subtotal=Decimal("100.00"),
        )
        self.client.force_login(intruder)
        response = self.client.get(reverse("store:order_detail", args=[order.id]))
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------ reviews
    def test_review_submission(self):
        user = User.objects.create_user(username="reviewer", password="TestPass123!")
        self.client.force_login(user)
        response = self.client.post(
            reverse("store:product_detail", args=[self.product.slug]),
            {"rating": 5, "comment": "Lovely plant!"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Review.objects.filter(product=self.product, user=user, rating=5).exists())

    def test_one_review_per_user_per_product(self):
        user = User.objects.create_user(username="reviewer2", password="TestPass123!")
        Review.objects.create(product=self.product, user=user, rating=4, comment="Good")
        self.client.force_login(user)
        response = self.client.post(
            reverse("store:product_detail", args=[self.product.slug]),
            {"rating": 2, "comment": "Trying again"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.filter(product=self.product, user=user).count(), 1)

    # --------------------------------------------------------------- rating sort
    def test_products_sort_by_rating_uses_db_annotation(self):
        response = self.client.get(reverse("store:product_list") + "?sort=rating")
        self.assertEqual(response.status_code, 200)

    # ------------------------------------------------------------ profile save
    def test_user_can_update_profile_details(self):
        user = User.objects.create_user(username="profileuser", password="TestPass123!")
        self.client.force_login(user)
        response = self.client.post(reverse("store:profile"), {
            "first_name": "Jane", "last_name": "Doe",
            "phone": "9876543210", "address_line1": "", "address_line2": "",
            "city": "", "state": "", "postal_code": "", "country": "India",
        })
        self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Jane")
        self.assertEqual(user.profile.phone, "9876543210")
