from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from apps.wishlist.models import Wishlist, WishlistItem
from apps.products.models import Product


@login_required
def wishlist_list(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    items = wishlist.items.select_related("product").prefetch_related("product__images").order_by("-added_at")
    return render(request, "wishlist/list.html", {"wishlist": wishlist, "items": items})


@login_required
@require_POST
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    item = wishlist.items.filter(product=product).first()

    if item:
        item.delete()
        in_wishlist = False
        msg = f"{product.name} retire de vos favoris"
    else:
        WishlistItem.objects.create(
            wishlist=wishlist,
            product=product,
            price_at_addition=product.effective_price,
        )
        in_wishlist = True
        msg = f"{product.name} ajoute a vos favoris"

    messages.success(request, msg)
    return redirect(request.META.get("HTTP_REFERER", "/"))
