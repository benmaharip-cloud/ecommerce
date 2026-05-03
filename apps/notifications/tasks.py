from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


@shared_task
def send_order_confirmation_email(order_id):
    from apps.orders.models import Order
    try:
        order = Order.objects.select_related('user').prefetch_related('items').get(id=order_id)
        send_mail(
            subject=f'Confirmation commande {order.reference}',
            message=f'Votre commande {order.reference} est confirmee. Merci !',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
        )
    except Exception as e:
        print(f'Erreur email commande: {e}')


@shared_task
def send_shipping_notification(order_id):
    from apps.orders.models import Order
    try:
        order = Order.objects.select_related('user').get(id=order_id)
        send_mail(
            subject=f'Votre commande {order.reference} est expediee !',
            message=f'Votre commande est en route.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
        )
    except Exception as e:
        print(f'Erreur email livraison: {e}')


@shared_task
def send_abandoned_cart_email(user_id):
    from apps.users.models import User
    try:
        user = User.objects.get(id=user_id)
        send_mail(
            subject='Votre panier vous attend !',
            message='Vous avez des articles dans votre panier.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
    except Exception as e:
        print(f'Erreur email panier abandonne: {e}')


@shared_task
def send_price_drop_notification(product_id):
    from apps.products.models import Product
    from apps.wishlist.models import WishlistItem
    from apps.notifications.models import Notification
    try:
        product = Product.objects.get(id=product_id)
        items = WishlistItem.objects.filter(product=product, notify_price_drop=True).select_related('wishlist__user')
        for item in items:
            user = item.wishlist.user
            Notification.objects.create(
                user=user,
                notification_type='price_drop',
                title=f'Prix reduit : {product.name}',
                message=f'Le prix est passe a {product.effective_price} FCFA !',
                link=f'/produits/{product.slug}/',
            )
    except Exception as e:
        print(f'Erreur notification baisse prix: {e}')


@shared_task
def send_push_notification(user_id, title, body, data=None):
    pass


@shared_task
def send_sms_notification(phone, message):
    print(f'SMS vers {phone}: {message}')


@shared_task
def check_wishlist_back_in_stock():
    pass


def notifications(request):
    if request.user.is_authenticated:
        count = request.user.notifications.filter(is_read=False).count()
        return {'unread_notifications_count': count}
    return {'unread_notifications_count': 0}
