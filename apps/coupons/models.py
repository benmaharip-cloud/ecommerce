from django.db import models
from django.conf import settings
from django.utils import timezone


class Coupon(models.Model):
    TYPE_CHOICES = [
        ('percent', 'Pourcentage'),
        ('fixed', 'Montant fixe'),
        ('free_shipping', 'Livraison gratuite'),
    ]

    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, blank=True)
    discount_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='percent')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    current_uses = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    first_purchase_only = models.BooleanField(default=False)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True,
        help_text='Vide = tous les utilisateurs'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self, user=None, order_total=0):
        if not self.is_active:
            return False, 'Coupon inactif'
        if self.valid_until and timezone.now() > self.valid_until:
            return False, 'Coupon expiré'
        if self.max_uses and self.current_uses >= self.max_uses:
            return False, 'Coupon épuisé'
        if order_total < float(self.minimum_order_amount):
            return False, f'Montant minimum requis : {self.minimum_order_amount} FCFA'
        if self.first_purchase_only and user:
            from apps.orders.models import Order
            if Order.objects.filter(user=user, payment_status='paid').exists():
                return False, 'Coupon réservé au premier achat'
        return True, 'Valide'

    def apply(self, total):
        if self.discount_type == 'percent':
            return float(total) * float(self.discount_value) / 100
        elif self.discount_type == 'fixed':
            return min(float(self.discount_value), float(total))
        return 0

    def use(self):
        self.current_uses += 1
        self.save()

    def __str__(self):
        return f'{self.code} ({self.get_discount_type_display()})'

    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
        ordering = ['-created_at']
