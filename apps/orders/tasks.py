from celery import shared_task

@shared_task
def daily_sales_report():
    from apps.orders.models import Order
    from django.utils import timezone
    from django.core.mail import send_mail
    from django.conf import settings
    
    today = timezone.now().date()
    orders = Order.objects.filter(created_at__date=today)
    total = sum(o.total_price for o in orders if hasattr(o, 'total_price'))
    
    send_mail(
        subject=f"📊 Rapport ventes du {today}",
        message=f"Commandes aujourd'hui: {orders.count()}\nTotal: {total} FCFA",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.DEFAULT_FROM_EMAIL],
        fail_silently=True,
    )
    return f"Rapport envoyé: {orders.count()} commandes"
