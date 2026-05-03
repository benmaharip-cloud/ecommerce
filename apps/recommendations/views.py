from django.shortcuts import render
from django.http import JsonResponse
from .engine import get_recommendations
from apps.products.models import Product

def recommendations_api(request):
    """API JSON pour les recommandations (AJAX)."""
    product_id = request.GET.get("product_id")
    product = None
    if product_id:
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            pass
    recs = get_recommendations(user=request.user if request.user.is_authenticated else None,
                               product=product, limit=6)
    data = []
    for p in recs:
        data.append({
            "id": p.pk,
            "name": p.name,
            "price": str(p.price),
            "image": p.images.first().image.url if p.images.exists() else "",
            "url": f"/produits/{p.slug}/",
        })
    return JsonResponse({"recommendations": data})
