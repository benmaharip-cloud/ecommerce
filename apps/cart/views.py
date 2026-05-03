from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils.translation import gettext as _
from apps.cart.models import Cart
from apps.products.models import Product
from apps.coupons.models import Coupon


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/detail.html', {'cart': cart})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    variant_id = request.POST.get('variant_id')

    if product.stock < quantity:
        messages.error(request, _('Stock insuffisant'))
        return redirect(request.META.get('HTTP_REFERER', '/'))

    cart.add(product, quantity=quantity, variant_id=variant_id)
    messages.success(request, _(f'"{product.name}" ajouté au panier'))

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': len(cart)})
    return redirect('cart:detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    variant_id = request.POST.get('variant_id')
    cart.remove(product_id, variant_id)
    return redirect('cart:detail')


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    variant_id = request.POST.get('variant_id')
    cart.update_quantity(product_id, quantity, variant_id)
    return redirect('cart:detail')


@require_POST
def apply_coupon(request):
    cart = Cart(request)
    code = request.POST.get('coupon_code', '').strip().upper()
    try:
        coupon = Coupon.objects.get(code=code, is_active=True)
        valid, msg = coupon.is_valid(user=request.user, order_total=cart.subtotal)
        if valid:
            cart.apply_coupon(coupon)
            messages.success(request, _(f'Coupon "{code}" appliqué ! Réduction : {coupon.discount_value}'))
        else:
            messages.error(request, msg)
    except Coupon.DoesNotExist:
        messages.error(request, _('Code coupon invalide'))
    return redirect('cart:detail')


@require_POST
def remove_coupon(request):
    cart = Cart(request)
    cart.remove_coupon()
    messages.success(request, _('Coupon retiré'))
    return redirect('cart:detail')
