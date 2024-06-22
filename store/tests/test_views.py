from django.test import TestCase
from django.urls import reverse

from accounts.models import Shopper
from store.models import Product


class StoreTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            # name="basket ebene",
            price=49,
            stock=4,
            description="Jolie paire de basket sombre non salissante",
        )

    # tester si les produits s'affiche sur la page d'accueil
    def test_products_are_shown_on_index_page(self):
        resp = self.client.get(reverse("index"))

        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.product.name, str(resp.content))
        # self.assertIn(self.product.thumbnail_url(), str(resp.content))

    # tester la connexion d'accueil
    def test_connexion_link_shown_when_user_not_connected(self):
        resp = self.client.get(reverse("index"))
        self.assertIn("Connexion", str(resp.content))

    def test_redirect_when_anonymous_user_access_cart_views(self):
        resp = self.client.get(reverse("store:cart"))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, f"{reverse('accounts:login')}?next={reverse('store:cart')}", status_code=302)


class storeLoggedInTest(TestCase):
    def setUp(self):
        self.user = Shopper.objects.create_user(
            email="amadeus@gmail.com",
            first_name="Amadeus",
            last_name="Mozart",
            password="123456789"
        )

    def test_valid_login(self):
        data = {'email': 'amadeus@gmail.com', 'password': '123456789'}
        resp = self.client.post(reverse('accounts:login'), data=data)
        self.assertEqual(resp.status_code, 200)  # 302

        # resp = self.client.get(reverse('index'))
        # self.assertIn("Profil", str(resp.content))

    def test_invalid_login(self):
        data = {'email': 'amadeus@gmail.com', 'password': '1234'}
        resp = self.client.post(reverse('accounts:login'), data=data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "accounts/login.html")

    def test_profile_change(self):
        self.client.login(email="amadeus@gmail.com",
                          password="123456789")

        data = {
            "email": "amadeus@gmail.com",
            "password": "123456789",
            "first_name": "Amadeus",
            "last_name": "Salieri"
        }

        resp = self.client.post(reverse('accounts:profile'), data=data)
        self.assertEqual(resp.status_code, 302)
        amadeus = Shopper.objects.get(email="amadeus@gmail.com")
        self.assertEqual(amadeus.last_name, "Salieri")
