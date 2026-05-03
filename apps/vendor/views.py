from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from apps.orders.models import Order, OrderItem
from apps.products.models import Product
from apps.reviews.models import Review


class VendorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in ("vendor", "admin")

    def handle_no_permission(self):
        from django.shortcuts import redirect
        from django.contrib import messages
        if not self.request.user.is_authenticated:
            return redirect(f"/compte/connexion/?next={self.request.path}")
        # Client connecté mais pas vendeur
        messages.warning(
            self.request,
            "Vous n\'avez pas accès au tableau de bord vendeur. "
            "Contactez-nous pour devenir vendeur."
        )
        return redirect("/")


class VendorDashboardView(VendorRequiredMixin, TemplateView):
    template_name = "vendor/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        vendor = self.request.user
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)

        vendor_products = Product.objects.filter(vendor=vendor)
        vendor_orders = Order.objects.filter(
            items__product__vendor=vendor
        ).distinct()

        # Stats ce mois vs mois dernier
        monthly_rev = vendor_orders.filter(
            created_at__gte=month_start, payment_status="paid"
        ).aggregate(total=Sum("total"))["total"] or 0

        last_rev = vendor_orders.filter(
            created_at__gte=last_month_start,
            created_at__lt=month_start,
            payment_status="paid"
        ).aggregate(total=Sum("total"))["total"] or 0

        monthly_orders = vendor_orders.filter(created_at__gte=month_start).count()
        last_orders = vendor_orders.filter(
            created_at__gte=last_month_start, created_at__lt=month_start
        ).count()

        def pct_change(new, old):
            if old == 0: return 100 if new > 0 else 0
            return round((new - old) / old * 100)

        ctx["stats"] = {
            "total_products": vendor_products.count(),
            "active_products": vendor_products.filter(is_active=True).count(),
            "total_orders": vendor_orders.count(),
            "monthly_orders": monthly_orders,
            "orders_change": pct_change(monthly_orders, last_orders),
            "total_revenue": vendor_orders.filter(
                payment_status="paid"
            ).aggregate(total=Sum("total"))["total"] or 0,
            "monthly_revenue": monthly_rev,
            "revenue_change": pct_change(monthly_rev, last_rev),
            "avg_rating": Review.objects.filter(
                product__vendor=vendor, is_approved=True
            ).aggregate(avg=Avg("rating"))["avg"] or 0,
            "total_reviews": Review.objects.filter(
                product__vendor=vendor, is_approved=True
            ).count(),
            "low_stock_count": vendor_products.filter(stock__lt=5, is_active=True).count(),
            "pending_orders": vendor_orders.filter(status="pending").count(),
        }

        # Graphique revenus 7 derniers jours
        daily_revenue = []
        daily_labels = []
        for i in range(6, -1, -1):
            day = now - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day.replace(hour=23, minute=59, second=59)
            rev = vendor_orders.filter(
                created_at__range=(day_start, day_end),
                payment_status="paid"
            ).aggregate(total=Sum("total"))["total"] or 0
            daily_revenue.append(float(rev))
            daily_labels.append(day.strftime("%d/%m"))

        ctx["chart_labels"] = daily_labels
        ctx["chart_data"] = daily_revenue

        # Top produits
        ctx["top_products"] = OrderItem.objects.filter(
            product__vendor=vendor
        ).values("product__name", "product__slug", "product__id").annotate(
            total_sold=Sum("quantity")
        ).order_by("-total_sold")[:5]

        # Commandes récentes
        ctx["recent_orders"] = vendor_orders.select_related(
            "user"
        ).prefetch_related("items").order_by("-created_at")[:8]

        # Stock faible
        ctx["low_stock"] = vendor_products.filter(
            stock__lt=10, is_active=True
        ).order_by("stock")[:8]

        # Derniers avis
        ctx["recent_reviews"] = Review.objects.filter(
            product__vendor=vendor, is_approved=True
        ).select_related("user", "product").order_by("-created_at")[:5]

        return ctx


class VendorProductListView(VendorRequiredMixin, ListView):
    template_name = "vendor/products.html"
    context_object_name = "products"
    paginate_by = 20

    def get_queryset(self):
        qs = Product.objects.filter(vendor=self.request.user).order_by("-created_at")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(name__icontains=q)
        status = self.request.GET.get("status")
        if status == "active":
            qs = qs.filter(is_active=True)
        elif status == "inactive":
            qs = qs.filter(is_active=False)
        elif status == "low_stock":
            qs = qs.filter(stock__lt=10)
        return qs


class VendorOrderListView(VendorRequiredMixin, ListView):
    template_name = "vendor/orders.html"
    context_object_name = "orders"
    paginate_by = 20

    def get_queryset(self):
        qs = Order.objects.filter(
            items__product__vendor=self.request.user
        ).distinct().select_related("user").order_by("-created_at")
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs


class VendorStatsApiView(VendorRequiredMixin, View):
    def get(self, request):
        vendor = request.user
        now = timezone.now()
        period = request.GET.get("period", "7")
        days = int(period)
        labels, data = [], []
        for i in range(days - 1, -1, -1):
            day = now - timedelta(days=i)
            s = day.replace(hour=0, minute=0, second=0, microsecond=0)
            e = day.replace(hour=23, minute=59, second=59)
            rev = Order.objects.filter(
                items__product__vendor=vendor,
                created_at__range=(s, e),
                payment_status="paid"
            ).distinct().aggregate(t=Sum("total"))["t"] or 0
            labels.append(day.strftime("%d/%m"))
            data.append(float(rev))
        return JsonResponse({"labels": labels, "data": data})


from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

class VendorTasksView(LoginRequiredMixin, View):
    def get(self, request):
        from django_celery_beat.models import PeriodicTask
        from django.shortcuts import render as django_render
        tasks = PeriodicTask.objects.all().order_by('name')
        context = {
            'tasks': tasks,
            'total_tasks': tasks.count(),
            'active_tasks': tasks.filter(enabled=True).count(),
            'inactive_tasks': tasks.filter(enabled=False).count(),
            'crontab_tasks': tasks.exclude(crontab=None).count(),
        }
        return django_render(request, 'vendor/tasks.html', context)
