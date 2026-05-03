from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from apps.reviews.models import Review
from apps.products.models import Product


@login_required
@require_POST
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    rating = int(request.POST.get("rating", 5))
    content = request.POST.get("content", "").strip()
    if not content:
        messages.error(request, "Le contenu de l'avis est requis")
        return redirect(f"/produits/{product.slug}/")
    review, created = Review.objects.get_or_create(
        product=product, user=request.user,
        defaults={"rating": rating, "content": content, "is_approved": True}
    )
    if not created:
        review.rating = rating
        review.content = content
        review.is_approved = True
        review.save()
        messages.success(request, "Votre avis a ete mis a jour")
    else:
        messages.success(request, "Votre avis a ete ajoute avec succes")
    return redirect(f"/produits/{product.slug}/")


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_slug = review.product.slug
    review.delete()
    messages.success(request, "Avis supprime")
    return redirect(f"/produits/{product_slug}/")
