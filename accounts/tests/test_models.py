from django.test import TestCase

from accounts.models import Shopper
from store.models import Product


class UserTest(TestCase):
    def setUp(self):
        Product.objects.create(
            name="Basket ébène",
            price=49,
            stock=4,
            description="Jolie paire de basket sombre non salissante",
        )
        self.user: Shopper = Shopper.objects.create_user(
            email="test@gmail.com",
            password="123456789"
        )

    # verifier après ajout d'éléments dans panier l'article dans le panier
    def test_add_to_cart(self):
        self.user.add_to_cart(slug="basket-ebene")
        self.assertEqual(self.user.cart.orders.count(), 1)
        # self.assertEqual(self.user.cart.orders.count(), 3)
        self.assertEqual(self.user.cart.orders.first().product.slug, "basket-ebene")
        self.user.add_to_cart(slug="basket-ebene")
        self.assertEqual(self.user.cart.orders.first().quantity, 2)
