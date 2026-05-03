from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Avg, Count
from django.shortcuts import get_object_or_404
from apps.products.models import Product, Category
from apps.recommendations.models import RecommendationEngine, ProductView
from apps.cart.models import Cart


class HomeView(TemplateView):
    template_name = 'products/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['featured_products'] = Product.objects.filter(is_featured=True, is_active=True, stock__gt=0)[:8]
        ctx['new_arrivals'] = Product.objects.filter(is_active=True, stock__gt=0).order_by('-created_at')[:8]
        ctx['categories'] = Category.objects.filter(is_active=True, parent=None).order_by('order')[:8]
        ctx['recommended'] = RecommendationEngine.get_recommendations(user=self.request.user, limit=8)

        # Offres du jour (produits avec réduction)
        from django.db.models import F, ExpressionWrapper, FloatField
        ctx['discounted_products'] = Product.objects.filter(
            is_active=True, stock__gt=0, discount_price__isnull=False
        ).order_by('-is_featured')[:8]

        # Best-sellers
        from apps.orders.models import OrderItem
        from django.db.models import Sum
        bestseller_ids = OrderItem.objects.values('product').annotate(
            total_sold=Sum('quantity')
        ).order_by('-total_sold').values_list('product', flat=True)[:6]
        
        # Conserver l'ordre des best-sellers
        from django.db.models import Case, When, IntegerField
        if bestseller_ids:
            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(bestseller_ids)], output_field=IntegerField())
            best = list(Product.objects.filter(pk__in=bestseller_ids, is_active=True).annotate(order=preserved).order_by('order'))
            # Ajouter total_sold à chaque produit
            sold_map = {row['product']: row['total_sold'] for row in OrderItem.objects.values('product').annotate(total_sold=Sum('quantity'))}
            for p in best:
                p.total_sold = sold_map.get(p.pk, 0)
            ctx['best_sellers'] = best
        else:
            ctx['best_sellers'] = Product.objects.filter(is_active=True).order_by('-views')[:6]

        # Coupons actifs
        from apps.coupons.models import Coupon
        from django.utils import timezone
        ctx['active_coupons'] = Coupon.objects.filter(
            is_active=True,
            valid_from__lte=timezone.now(),
            valid_until__gte=timezone.now()
        ).order_by('-discount_value')[:5]
        # Stats pour la page d'accueil
        from apps.users.models import User
        from apps.orders.models import Order
        ctx['total_products'] = Product.objects.filter(is_active=True).count()
        ctx['total_orders'] = Order.objects.count()
        ctx['total_clients'] = User.objects.filter(is_active=True).count()
        # Stats pour la page d'accueil
        from apps.users.models import User
        from apps.orders.models import Order
        ctx['total_products'] = Product.objects.filter(is_active=True).count()
        ctx['total_orders'] = Order.objects.count()
        ctx['total_clients'] = User.objects.filter(is_active=True).count()
        return ctx


class ProductListView(ListView):
    template_name = 'products/list.html'
    context_object_name = 'products'
    paginate_by = 16

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True)
        q = self.request.GET.get('q')
        category_slug = self.request.GET.get('category')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        rating = self.request.GET.get('rating')
        sort = self.request.GET.get('sort', '-created_at')

        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)
        if rating:
            qs = qs.annotate(avg_rating=Avg('reviews__rating')).filter(avg_rating__gte=rating)

        sort_options = {
            'price_asc': 'price', 'price_desc': '-price',
            'newest': '-created_at', 'popular': '-orderitem__count',
            'rating': '-avg_rating',
        }
        qs = qs.order_by(sort_options.get(sort, '-created_at'))
        return qs.distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.filter(is_active=True)
        return ctx


class ProductDetailView(DetailView):
    template_name = 'products/detail.html'
    model = Product
    context_object_name = 'product'
    slug_field = 'slug'

    def get_object(self):
        product = get_object_or_404(Product, slug=self.kwargs['slug'], is_active=True)
        # Enregistrer la vue pour les recommandations
        if self.request.user.is_authenticated:
            try:
                pv, created = ProductView.objects.get_or_create(user=self.request.user, product=product)
                if not created:
                    pv.view_count += 1
                    pv.save()
            except Exception:
                pass
        return product

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product = self.object
        ctx['reviews'] = product.reviews.filter(is_approved=True).select_related('user').prefetch_related('images')[:10]
        ctx['similar_products'] = RecommendationEngine.get_recommendations(product=product, limit=6)
        ctx['in_wishlist'] = False
        if self.request.user.is_authenticated:
            ctx['in_wishlist'] = self.request.user.wishlist.products.filter(id=product.id).exists() \
                if hasattr(self.request.user, 'wishlist') else False
        return ctx

from django.views import View
from django.http import JsonResponse
from django.core.files.storage import default_storage
import base64, json

class ImageSearchView(View):
    def post(self, request):
        try:
            image = request.FILES.get('image')
            if not image:
                return JsonResponse({'error': 'Aucune image'}, status=400)
            
            image_name = image.name.lower()
            
            # Correspondance mot-clé → slug catégorie
            keywords = {
                'electronique': ['phone', 'iphone', 'samsung', 'laptop', 'computer', 
                                 'ordinateur', 'tablet', 'ipad', 'casque', 'bluetooth',
                                 'headphone', 'earphone', 'camera', 'tv', 'ecran'],
                'chaussures': ['shoe', 'chaussure', 'sneaker', 'boot', 'sandale', 
                               'sandal', 'nike', 'adidas', 'basket'],
                'accessoires': ['bag', 'sac', 'watch', 'montre', 'wallet', 
                                'portefeuille', 'bracelet', 'jewelry', 'bijou'],
                'veste': ['shirt', 'veste', 'jacket', 'habit', 'vetement', 
                          'clothes', 'robe', 'pantalon', 'jean'],
            }
            
            matched_slug = None
            for slug, kws in keywords.items():
                for kw in kws:
                    if kw in image_name:
                        matched_slug = slug
                        break
                if matched_slug:
                    break
            
            return JsonResponse({
                'category': matched_slug or '',
                'count': 1
            })
        except Exception as e:
            return JsonResponse({'error': str(e), 'category': ''}, status=200)


from django.http import JsonResponse as _JsonResponse

def product_preview(request, slug):
    from django.shortcuts import get_object_or_404
    from .models import Product
    p = get_object_or_404(Product, slug=slug)
    return _JsonResponse({
        "id": p.pk,
        "name": p.name,
        "price": str(p.price),
        "discount_price": str(p.discount_price) if p.discount_price else None,
        "description": (p.description or "")[:300],
        "image": p.images.first().image.url if p.images.exists() else "",
        "url": f"/produits/{p.slug}/",
    })
