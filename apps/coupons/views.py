

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from .models import Coupon

@login_required
def my_coupons(request):
    coupons = Coupon.objects.filter(
        is_active=True,
        valid_from__lte=timezone.now(),
        valid_until__gte=timezone.now()
    ).order_by('-discount_value')
    return render(request, "coupons/my_coupons.html", {"coupons": coupons})

def validate_coupon(request):
    code = request.GET.get("code", "").strip().upper()
    try:
        coupon = Coupon.objects.get(code=code, is_active=True)
        now = timezone.now()
        if coupon.valid_from > now:
            return JsonResponse({"valid": False, "error": "Ce coupon n\'est pas encore actif"})
        if coupon.valid_until < now:
            return JsonResponse({"valid": False, "error": "Ce coupon a expiré"})
        if coupon.max_uses > 0 and coupon.current_uses >= coupon.max_uses:
            return JsonResponse({"valid": False, "error": "Ce coupon a atteint sa limite d\'utilisation"})
        return JsonResponse({
            "valid": True,
            "code": coupon.code,
            "discount_type": coupon.discount_type,
            "discount_value": str(coupon.discount_value),
            "description": coupon.description,
            "minimum_order_amount": str(coupon.minimum_order_amount),
        })
    except Coupon.DoesNotExist:
        return JsonResponse({"valid": False, "error": "Code promo invalide"})
