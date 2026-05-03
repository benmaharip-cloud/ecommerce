from django.db import models
from django.conf import settings


class Wishlist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField('products.Product', through='WishlistItem')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Wishlist de {self.user}'


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    price_at_addition = models.DecimalField(max_digits=12, decimal_places=2)
    notify_price_drop = models.BooleanField(default=True)
    notify_back_in_stock = models.BooleanField(default=True)

    class Meta:
        unique_together = ['wishlist', 'product']
        ordering = ['-added_at']
