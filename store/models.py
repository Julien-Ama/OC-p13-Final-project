from django.db import models
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from shop.settings import AUTH_USER_MODEL

# Create your models here.
"""
Product
- Nom
- Prix
- La quantité en stock
- Description
- Image
"""


class Product(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128, blank=True)
    price = models.FloatField(default=0.0)
    stock = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="products", blank=True, null=True)
    stripe_id = models.CharField(max_length=98, blank=True)

    def __str__(self):
        return f"{self.name} ({self.stock})"

    def get_absolute_url(self):
        return reverse("store:product", kwargs={"slug": self.slug})

    # generation automatique de slug
    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.name)
        super().save(*args, **kwargs)

    def thumbnail_url(self):
        return self.thumbnail.url if self.thumbnail else static("img/default.png")


"""
Article (Order)
- Utilisateur
- Produit
- Quantité
- Commandé ou non
"""


class Order(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"


"""
Panier (Cart)
- Utilisateur
- Articles
- Commandé ou non
- Date de la commande
"""


class Cart(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE)  # ForeignKey(unique=True)
    orders = models.ManyToManyField(Order)
    ordered = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        if self.user:
            return str(self.user.username)

        else:
            return "Cart (No user)"

    def delete(self, *args, **kwargs):
        for order in self.orders.all():
            order.ordered = True
            order.ordered_date = timezone.now()
            order.save()

        self.orders.clear()
        super().delete(*args, **kwargs)
