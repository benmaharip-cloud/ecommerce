from django.db import models
from django.conf import settings
import uuid


class DeliveryZone(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_days = models.PositiveSmallIntegerField(default=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name} — {self.city} ({self.price} FCFA)'

    class Meta:
        verbose_name = 'Zone de livraison'
        verbose_name_plural = 'Zones de livraison'


class Delivery(models.Model):
    STATUS_CHOICES = [
        ('preparing', 'Préparation'),
        ('picked_up', 'Récupéré'),
        ('in_transit', 'En transit'),
        ('out_for_delivery', 'En cours de livraison'),
        ('delivered', 'Livré'),
        ('failed', 'Échec'),
    ]

    order = models.OneToOneField(
        'orders.Order', on_delete=models.CASCADE, related_name='delivery'
    )
    zone = models.ForeignKey(DeliveryZone, on_delete=models.SET_NULL, null=True, blank=True)
    driver_name = models.CharField(max_length=100, blank=True)
    driver_phone = models.CharField(max_length=20, blank=True)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='preparing')
    tracking_code = models.CharField(max_length=50, unique=True, blank=True)
    estimated_arrival = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = f'TRK-{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Livraison #{self.tracking_code} — {self.get_status_display()}'

    class Meta:
        verbose_name = 'Livraison'
        verbose_name_plural = 'Livraisons'
