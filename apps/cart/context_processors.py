def cart(request):
    from apps.cart.models import Cart
    return {'cart': Cart(request)}
