from django.db import models
from django.conf import settings


class ProductView(models.Model):
    """Historique de navigation pour les recommandations IA"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='product_views')
    session_key = models.CharField(max_length=40, blank=True)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='views')
    view_count = models.PositiveIntegerField(default=1)
    last_viewed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['user', 'product'], ['session_key', 'product']]


class RecommendationEngine:
    """Moteur de recommandations basé sur collaborative filtering et historique"""

    @staticmethod
    def get_recommendations(user=None, product=None, limit=10):
        from apps.products.models import Product
        from apps.orders.models import OrderItem

        recommendations = []

        # 1. Produits de la même catégorie
        if product:
            similar = Product.objects.filter(
                category=product.category,
                is_active=True,
                stock__gt=0,
            ).exclude(id=product.id).order_by('-created_at')[:limit]
            recommendations.extend(similar)

        # 2. Collaborative filtering — produits achetés ensemble
        if product:
            orders_with_product = OrderItem.objects.filter(product=product).values_list('order_id', flat=True)
            bought_together = Product.objects.filter(
                orderitem__order_id__in=orders_with_product,
                is_active=True,
            ).exclude(id=product.id).annotate(
                co_count=models.Count('id')
            ).order_by('-co_count')[:limit]
            recommendations.extend(bought_together)

        # 3. Basé sur l'historique utilisateur
        if user and user.is_authenticated:
            viewed_categories = ProductView.objects.filter(user=user).values_list('product__category_id', flat=True)
            user_based = Product.objects.filter(
                category_id__in=viewed_categories,
                is_active=True,
                stock__gt=0,
            ).order_by('-created_at')[:limit]
            recommendations.extend(user_based)

            # Produits achetés par utilisateurs similaires
            user_purchases = OrderItem.objects.filter(order__user=user).values_list('product_id', flat=True)
            similar_users = OrderItem.objects.filter(
                product_id__in=user_purchases
            ).values_list('order__user_id', flat=True).distinct().exclude(order__user=user)

            collab = Product.objects.filter(
                orderitem__order__user_id__in=similar_users,
                is_active=True,
            ).exclude(
                id__in=user_purchases
            ).annotate(score=models.Count('id')).order_by('-score')[:limit]
            recommendations.extend(collab)

        # 4. Tendances — produits les plus vendus
        trending = Product.objects.filter(is_active=True, stock__gt=0).annotate(
            sales_count=models.Count('orderitem')
        ).order_by('-sales_count')[:limit]
        recommendations.extend(trending)

        # Dédoublonner et limiter
        seen = set()
        unique = []
        for p in recommendations:
            if p.id not in seen:
                seen.add(p.id)
                unique.append(p)
            if len(unique) >= limit:
                break
        return unique
