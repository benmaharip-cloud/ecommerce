from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from apps.users.models import User, Address
from apps.loyalty.models import LoyaltyAccount


def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone', '')

        if User.objects.filter(email=email).exists():
            messages.error(request, _('Un compte existe déjà avec cet email'))
            return render(request, 'users/register.html')

        user = User.objects.create_user(
            email=email, password=password,
            first_name=first_name, last_name=last_name, phone=phone,
        )
        # Créer compte fidélité automatiquement
        LoyaltyAccount.objects.create(user=user)
        # Connecter l'utilisateur
        login(request, user, backend='apps.users.backends.EmailBackend')
        messages.success(request, _(f'Bienvenue {first_name} ! Votre compte a été créé.'))
        return redirect('products:home')

    return render(request, 'users/register.html')


@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone = request.POST.get('phone', user.phone)
        user.preferred_language = request.POST.get('preferred_language', user.preferred_language)
        user.preferred_currency = request.POST.get('preferred_currency', user.preferred_currency)
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        user.save()
        messages.success(request, _('Profil mis à jour avec succès'))
        return redirect('users:profile')

    loyalty = getattr(user, 'loyalty', None)
    orders = user.orders.order_by('-created_at')[:5]
    addresses = user.addresses.all()

    return render(request, 'users/profile.html', {
        'user': user,
        'loyalty': loyalty,
        'recent_orders': orders,
        'addresses': addresses,
    })


@login_required
def my_coupons(request):
    from apps.coupons.models import Coupon
    from django.utils import timezone
    coupons = Coupon.objects.filter(
        is_active=True,
        valid_from__lte=timezone.now(),
        valid_until__gte=timezone.now()
    ).order_by('-discount_value')
    return render(request, "coupons/my_coupons.html", {"coupons": coupons})
