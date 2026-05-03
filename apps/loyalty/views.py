from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.loyalty.models import LoyaltyAccount, LoyaltyTransaction

@login_required
def loyalty_account(request):
    account, _ = LoyaltyAccount.objects.get_or_create(user=request.user)
    transactions = account.transactions.all()[:20]
    return render(request, 'loyalty/account.html', {'account': account, 'transactions': transactions})

@login_required
def redeem_points(request):
    if request.method == 'POST':
        points_str = request.POST.get('points', '').strip()
        if not points_str:
            messages.error(request, 'Veuillez entrer un nombre de points')
            return redirect('loyalty:account')
        points = int(points_str)
        try:
            discount = request.user.loyalty.redeem_points(points)
            messages.success(request, f'{points} points echanges contre {discount} FCFA')
        except ValueError as e:
            messages.error(request, str(e))
    return redirect('loyalty:account')
