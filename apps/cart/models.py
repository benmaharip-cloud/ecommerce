from django.db import models
from django.conf import settings
import json
import redis

r = redis.from_url(settings.REDIS_URL)


class Cart:
    """Panier stocké dans Redis — fonctionne pour utilisateurs connectés et anonymes."""

    def __init__(self, request):
        self.session = request.session
        self.user = request.user if request.user.is_authenticated else None
        self.key = f'cart:{self.user.id}' if self.user else f'cart:session:{self.session.session_key}'
        self._cart = self._load()

    def _load(self):
        data = r.get(self.key)
        return json.loads(data) if data else {}

    def _save(self):
        r.setex(self.key, 86400 * 7, json.dumps(self._cart))

    def add(self, product, quantity=1, variant_id=None):
        key = f'{product.id}_{variant_id or ""}'
        if key in self._cart:
            self._cart[key]['quantity'] += quantity
        else:
            self._cart[key] = {
                'product_id': product.id,
                'name': product.name,
                'price': str(product.effective_price),
                'quantity': quantity,
                'variant_id': variant_id,
                'image': product.images.filter(is_primary=True).first().image.url
                         if product.images.filter(is_primary=True).exists() else '',
            }
        self._save()

    def remove(self, product_id, variant_id=None):
        key = f'{product_id}_{variant_id or ""}'
        self._cart.pop(key, None)
        self._save()

    def update_quantity(self, product_id, quantity, variant_id=None):
        key = f'{product_id}_{variant_id or ""}'
        if key in self._cart:
            if quantity <= 0:
                self.remove(product_id, variant_id)
            else:
                self._cart[key]['quantity'] = quantity
                self._save()

    def clear(self):
        self._cart = {}
        r.delete(self.key)

    def apply_coupon(self, coupon):
        self._cart['coupon'] = {'code': coupon.code, 'discount': str(coupon.discount_value), 'type': coupon.discount_type}
        self._save()

    def remove_coupon(self):
        self._cart.pop('coupon', None)
        self._save()

    @property
    def items(self):
        return {k: v for k, v in self._cart.items() if k != 'coupon'}

    @property
    def coupon(self):
        return self._cart.get('coupon')

    @property
    def total_items(self):
        return sum(item['quantity'] for item in self.items.values())

    @property
    def subtotal(self):
        return sum(float(item['price']) * item['quantity'] for item in self.items.values())

    @property
    def discount_amount(self):
        if not self.coupon:
            return 0
        if self.coupon['type'] == 'percent':
            return self.subtotal * float(self.coupon['discount']) / 100
        return float(self.coupon['discount'])

    @property
    def total(self):
        return max(0, self.subtotal - self.discount_amount)

    def __len__(self):
        return self.total_items

    def __iter__(self):
        yield from self.items.values()


def cart(request):
    """Context processor — rend le panier disponible dans tous les templates."""
    return {'cart': Cart(request)}
