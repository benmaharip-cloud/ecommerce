from celery import shared_task
from django.utils import timezone

@shared_task
def expire_coupons():
    from apps.coupons.models import Coupon
    expired = Coupon.objects.filter(
        valid_until__lt=timezone.now(),
        is_active=True
    )
    count = expired.count()
    expired.update(is_active=False)
    return f"{count} codes promo expirés"
