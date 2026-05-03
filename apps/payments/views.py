from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from apps.orders.models import Order
from apps.loyalty.models import LoyaltyAccount

@login_required
def stripe_checkout_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "payments/checkout.html", {
        "order": order,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
        "client_secret": "simulated_secret",
        "simulation": True,
    })

@login_required
def stripe_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.payment_status = "paid"
    order.status = "confirmed"
    order.save()
    LoyaltyAccount.add_points_for_order(order)
    return redirect("/commandes/" + str(order.id) + "/confirmation/")

@csrf_exempt
def stripe_webhook(request):
    return HttpResponse(status=200)
