import stripe
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.shortcuts import get_object_or_404

from iso3166 import countries

from shop import settings
from store.models import Cart, Order, Product

stripe.api_key = settings.STRIPE_API_KEY

# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, password, **kwargs):
#         if not email:
#             raise ValueError("l'adresse email est obligatoire.")
#
#         email = self.normalize_email(email)
#         user = self.model(email=email, **kwargs)
#         user.set_password(password)
#         user.save()
#         return user
#
#     def create_superuser(self, email, password, **kwargs):
#         kwargs["is_staff"] = True
#         kwargs["is_superuser"] = True
#         kwargs["is_active"] = True
#
#         return self.create_user(email=email, password=password, **kwargs)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError("l'adresse email est obligatoire.")

        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()

        # Create Stripe Customer ID
        if not user.stripe_id:
            customer = stripe.Customer.create(email=user.email)
            user.stripe_id = customer.id
            user.save()

        return user

    def create_superuser(self, email, password=None, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_active', True)

        return self.create_user(email=email, password=password, **kwargs)


class Shopper(AbstractUser):
    username = None
    email = models.EmailField(max_length=240, unique=True)
    stripe_id = models.CharField(max_length=90, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def add_to_cart(self, slug):
        product = get_object_or_404(Product, slug=slug)
        cart, _ = Cart.objects.get_or_create(user=self)  # _ 2 éléments à gauche et à droite du symbole d'égalité
        order, created = Order.objects.get_or_create(user=self,
                                                     # ordered=False,
                                                     product=product)

        if created:
            cart.orders.add(order)
            cart.save()
        else:
            order.quantity += 1
            order.save()

        return cart


ADDRESS_FORMAT = """
{name}
{address_1}
{address_2}
{city}, {zip_code}
{country}
"""
# class ShippingAddress(models.Model):
#     user: Shopper = models.ForeignKey(Shopper, on_delete=models.CASCADE, related_name="addresses")
#     name = models.CharField(max_length=1024)
#     address_1 = models.CharField(max_length=1024, help_text="Adresse de voirie et numéro de rue.")
#     address_2 = models.CharField(max_length=1024, help_text="Bâtiment, étage, lieu-dit...", blank=True)
#     city = models.CharField(max_length=1024)
#     zip_code = models.CharField(max_length=24)
#     country = models.CharField(max_length=2, choices=[(c.alpha2.lower(), c.name) for c in countries])
#     default = models.BooleanField(default=False)
#     def __str__(self):
#         data = self.__dict__.copy()
#         data.update(country=self.get_country_display().upper())
#         return ADDRESS_FORMAT.format(**data).strip("\n")
#
#     def as_dict(self):
#         return {"city": self.city,
#                      "country": self.country,
#                      "line1": self.address_1,
#                      "line2": self.address_2,
#                      "postal_code": self.zip_code
#                 }
#
#     def set_default(self):
#         if not self.user.stripe_id:
#             raise ValueError(f"User {self.user.email} doesn't have a stripe Customer ID.")
#
#         self.user.addresses.update(default=False)
#         self.default = True
#         self.save()
#
#         stripe.Customer.modify(
#             self.user.stripe_id,
#             shipping={"name": self.name,
#                       "address": self.as_dict()},
#             address=self.as_dict()
#         )


class ShippingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses")
    name = models.CharField(max_length=1024)
    address_1 = models.CharField(max_length=1024, help_text="Adresse de voirie et numéro de rue.")
    address_2 = models.CharField(max_length=1024, help_text="Bâtiment, étage, lieu-dit...", blank=True)
    city = models.CharField(max_length=1024)
    zip_code = models.CharField(max_length=24)
    country = models.CharField(max_length=2, choices=[(c.alpha2.lower(), c.name) for c in countries])
    default = models.BooleanField(default=False)

    def __str__(self):
        data = self.__dict__.copy()
        data.update(country=self.get_country_display().upper())
        return ADDRESS_FORMAT.format(**data).strip("\n")

    def as_dict(self):
        return {
            "line1": self.address_1,
            "line2": self.address_2,
            "city": self.city,
            "postal_code": self.zip_code,
            "country": self.country.upper(),
        }

    def set_default(self):
        if not self.user.stripe_id:
            raise ValueError(f"User {self.user.email} doesn't have a stripe Customer ID.")

        self.user.addresses.update(default=False)
        self.default = True
        self.save()

        stripe.Customer.modify(
            self.user.stripe_id,
            shipping={"name": self.name,
                      "address": self.as_dict()}
        )
