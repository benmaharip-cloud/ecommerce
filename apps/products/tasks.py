from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def check_low_stock():
    from apps.products.models import Product
    low_stock = Product.objects.filter(stock__lte=5, is_active=True)
    if low_stock.exists():
        message = "Produits avec stock faible:\n\n"
        for p in low_stock:
            message += f"- {p.name}: {p.stock} restants\n"
        send_mail(
            subject="⚠️ ShopDjango - Stock faible",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=True,
        )
    return f"{low_stock.count()} produits stock faible"
