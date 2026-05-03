import os

# 1. Corriger apps/loyalty/views.py
loyalty_views = """from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from apps.loyalty.models import LoyaltyAccount, LoyaltyTransaction


@login_required
def loyalty_account(request):
    account, _ = LoyaltyAccount.objects.get_or_create(user=request.user)
    transactions = account.transactions.all()[:20]

    level_thresholds = {'bronze': 0, 'silver': 500, 'gold': 2000, 'platinum': 5000}
    next_levels = {'bronze': ('silver', 500), 'silver': ('gold', 2000), 'gold': ('platinum', 5000), 'platinum': (None, None)}
    next_level, next_threshold = next_levels[account.level]
    progress = 0
    if next_threshold:
        current_threshold = level_thresholds[account.level]
        progress = min(100, int((account.total_points_earned - current_threshold) / (next_threshold - current_threshold) * 100))

    return render(request, 'loyalty/account.html', {
        'account': account,
        'transactions': transactions,
        'next_level': next_level,
        'next_threshold': next_threshold,
        'progress': progress,
    })


@login_required
def redeem_points(request):
    if request.method == 'POST':
        points = int(request.POST.get('points', 0))
        account = request.user.loyalty
        try:
            discount = account.redeem_points(points)
            messages.success(request, _(f'{points} points echanges contre {discount} FCFA de reduction'))
        except ValueError as e:
            messages.error(request, str(e))
    return redirect('loyalty:account')
"""
open('apps/loyalty/views.py', 'w').write(loyalty_views)
print('OK - loyalty/views.py corrige')

# 2. Corriger apps/notifications/tasks.py — supprimer import wishlist
notif_tasks = """from celery import shared_task
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
"""
open('apps/notifications/tasks.py', 'w').write(notif_tasks)
print('OK - notifications/tasks.py corrige')

# 3. Corriger apps/notifications/context_processors.py
ctx = """def notifications(request):
    if request.user.is_authenticated:
        count = request.user.notifications.filter(is_read=False).count()
        return {'unread_notifications_count': count}
    return {'unread_notifications_count': 0}
"""
open('apps/notifications/context_processors.py', 'w').write(ctx)
print('OK - notifications/context_processors.py cree')

# 4. Corriger apps/cart/context_processors.py
cart_ctx = """def cart(request):
    from apps.cart.models import Cart
    return {'cart': Cart(request)}
"""
open('apps/cart/context_processors.py', 'w').write(cart_ctx)
print('OK - cart/context_processors.py cree')

# 5. Corriger ecommerce/urls.py — enlever doublons namespace
urls = """from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('rosetta/', include('rosetta.urls')),
    path('api/auth/', include('apps.users.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/cart/', include('apps.cart.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/reviews/', include('apps.reviews.urls')),
    path('api/wishlist/', include('apps.wishlist.urls')),
    path('api/coupons/', include('apps.coupons.urls')),
    path('api/delivery/', include('apps.delivery.urls')),
    path('api/loyalty/', include('apps.loyalty.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/vendor/', include('apps.vendor.urls')),
    path('api/recommendations/', include('apps.recommendations.urls')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('apps.products.web_urls')),
    path('panier/', include('apps.cart.web_urls')),
    path('compte/', include('apps.users.web_urls')),
    path('vendeur/', include('apps.vendor.web_urls')),
    path('chat/', include('apps.chat.urls')),
    path('commandes/', include(('apps.orders.web_urls', 'orders'), namespace='orders')),
    path('fidelite/', include(('apps.loyalty.urls', 'loyalty'), namespace='loyalty')),
    path('favoris/', include(('apps.wishlist.urls', 'wishlist'), namespace='wishlist')),
    path('mes-notifications/', include(('apps.notifications.urls', 'notifications'), namespace='notifications')),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""
open('ecommerce/urls.py', 'w').write(urls)
print('OK - ecommerce/urls.py corrige')

print()
print('Tous les fichiers corriges avec succes !')
