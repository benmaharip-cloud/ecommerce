from django.db.models import Count, Q
from apps.products.models import Product


def get_recommendations(user=None, product=None, limit=6):
    """
    Combine collaborative filtering (orders) + content (category/tags).
    Returns a queryset of Product.
    """
    exclude_ids = []
    if product:
        exclude_ids.append(product.pk)

    scored = {}

    # ── 1. Contenu : même catégorie ──────────────────────────────────────
    if product and product.category:
        qs = Product.objects.filter(
            category=product.category, is_active=True
        ).exclude(pk__in=exclude_ids)
        for p in qs[:20]:
            scored[p.pk] = scored.get(p.pk, 0) + 2

    # ── 2. Collaboratif : achetés ensemble ───────────────────────────────
    if product:
        try:
            from apps.orders.models import OrderItem
            co_orders = OrderItem.objects.filter(
                product=product
            ).values_list("order_id", flat=True)
            co_products = OrderItem.objects.filter(
                order_id__in=co_orders
            ).exclude(product=product).values("product").annotate(n=Count("product")).order_by("-n")
            for row in co_products[:20]:
                pid = row["product"]
                if pid not in exclude_ids:
                    scored[pid] = scored.get(pid, 0) + row["n"] * 3
        except Exception:
            pass

    # ── 3. Collaboratif : historique utilisateur ─────────────────────────
    if user and user.is_authenticated:
        try:
            from apps.orders.models import Order, OrderItem
            user_orders = Order.objects.filter(user=user).values_list("pk", flat=True)
            bought = OrderItem.objects.filter(
                order_id__in=user_orders
            ).values_list("product_id", flat=True)
            exclude_ids += list(bought)

            # Catégories préférées
            from apps.products.models import Category
            fav_cats = Product.objects.filter(
                pk__in=bought
            ).values("category").annotate(n=Count("category")).order_by("-n")[:3]
            for row in fav_cats:
                qs = Product.objects.filter(
                    category_id=row["category"], is_active=True
                ).exclude(pk__in=exclude_ids)
                for p in qs[:10]:
                    scored[p.pk] = scored.get(p.pk, 0) + row["n"]
        except Exception:
            pass

    # ── 4. Fallback : produits populaires ────────────────────────────────
    if not scored:
        return Product.objects.filter(is_active=True).exclude(
            pk__in=exclude_ids
        ).order_by("-created_at")[:limit]

    sorted_ids = sorted(scored, key=scored.get, reverse=True)[:limit]
    products = {p.pk: p for p in Product.objects.filter(pk__in=sorted_ids)}
    return [products[i] for i in sorted_ids if i in products]
