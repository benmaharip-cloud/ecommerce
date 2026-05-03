from celery import shared_task

@shared_task
def send_weekly_promo():
    from apps.users.models import User
    from apps.coupons.models import Coupon
    from django.core.mail import send_mail
    
    users = User.objects.filter(is_active=True).exclude(email='')
    coupon = Coupon.objects.filter(is_active=True).first()
    
    if not coupon:
        return "Aucun coupon actif"
    
    for user in users[:100]:
        send_mail(
            subject="🎁 ShopDjango - Offre spéciale cette semaine !",
            message=f"Bonjour {user.first_name},\n\nUtilisez le code {coupon.code} pour {coupon.discount_value}% de réduction !\n\nShopDjango",
            from_email='noreply@shopdjango.td',
            recipient_list=[user.email],
            fail_silently=True,
        )
    return f"Emails envoyés à {users.count()} utilisateurs"
