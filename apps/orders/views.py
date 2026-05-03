from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext as _
from apps.cart.models import Cart
from apps.orders.models import Order, OrderItem, OrderStatusHistory
from apps.delivery.models import DeliveryZone, Delivery
from apps.notifications.tasks import send_order_confirmation_email, send_sms_notification
import uuid


@login_required
def checkout(request):
    cart = Cart(request)
    if not len(cart):
        messages.warning(request, _('Votre panier est vide'))
        return redirect('cart:detail')

    zones = DeliveryZone.objects.filter(is_active=True)
    addresses = request.user.addresses.all()

    if request.method == 'POST':
        # Créer la commande
        zone_id = request.POST.get('zone_id')
        payment_method = request.POST.get('payment_method', 'cash')
        shipping_address = request.POST.get('shipping_address', '')
        shipping_city = request.POST.get('shipping_city', '')
        notes = request.POST.get('notes', '')

        shipping_cost = 0
        zone = None
        if zone_id:
            try:
                zone = DeliveryZone.objects.get(id=zone_id)
                shipping_cost = zone.price
            except DeliveryZone.DoesNotExist:
                pass

        order = Order.objects.create(
            user=request.user,
            payment_method=payment_method,
            shipping_name=request.user.full_name,
            shipping_phone=request.user.phone,
            shipping_address=shipping_address,
            shipping_city=shipping_city,
            subtotal=float(cart.subtotal),
            discount_amount=float(cart.discount_amount),
            shipping_cost=float(shipping_cost),
            total=cart.total + float(shipping_cost),
            coupon_code=cart.coupon['code'] if cart.coupon else '',
            notes=notes,
        )

        # Créer les articles
        from apps.products.models import Product
        for item in cart:
            product = Product.objects.get(id=item['product_id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=item['name'],
                quantity=item['quantity'],
                unit_price=item['price'],
            )
            # Décrémenter le stock
            product.stock -= item['quantity']
            product.save()

        # Créer livraison
        if zone:
            Delivery.objects.create(
                order=order,
                zone=zone,
                tracking_code=f'TRK-{uuid.uuid4().hex[:8].upper()}',
            )

        # Historique statut
        OrderStatusHistory.objects.create(order=order, status='pending', created_by=request.user)

        # Vider le panier
        cart.clear()

        # Si paiement cash — confirmation directe
        if payment_method == 'cash':
            order.status = 'confirmed'
            order.save()
            send_order_confirmation_email.delay(order.id)
            if request.user.phone:
                send_sms_notification.delay(request.user.phone, f'Commande {order.reference} confirmée ! Merci.')
            messages.success(request, _(f'Commande {order.reference} passée avec succès !'))
            return redirect('orders:confirmation', pk=order.id)

        # Paiement Stripe ou Mobile Money
        return redirect(f'/paiement/checkout/{order.id}/')

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'zones': zones,
        'addresses': addresses,
    })


class OrderListView(LoginRequiredMixin, ListView):
    template_name = 'orders/list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items').order_by('-created_at')


class OrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'orders/detail.html'
    model = Order
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['history'] = self.object.history.all()
        ctx['delivery'] = getattr(self.object, 'delivery', None)
        return ctx


@login_required
def order_confirmation(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'orders/confirmation.html', {'order': order})


def order_tracking(request):
    from django.shortcuts import render
    order = None
    error = None
    tracking_code = None
    ref = request.GET.get('ref', '').strip()
    
    if ref:
        try:
            from apps.orders.models import Order
            order = Order.objects.get(reference=ref)
            # Vérifier que c'est la commande du bon utilisateur
            if request.user.is_authenticated and order.user != request.user:
                error = "Cette commande ne vous appartient pas."
                order = None
            else:
                # Récupérer le code de suivi
                try:
                    tracking_code = order.delivery.tracking_code
                except:
                    tracking_code = None
        except:
            error = f"Aucune commande trouvée avec la référence '{ref}'."
    
    recent_orders = []
    if request.user.is_authenticated:
        from apps.orders.models import Order
        recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    return render(request, 'orders/tracking.html', {
        'order': order,
        'error': error,
        'tracking_code': tracking_code,
        'recent_orders': recent_orders,
    })
