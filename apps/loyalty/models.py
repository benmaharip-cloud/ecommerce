from django.db import models
from django.conf import settings


class LoyaltyAccount(models.Model):
    LEVEL_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Argent'),
        ('gold', 'Or'),
        ('platinum', 'Platine'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loyalty'
    )
    points = models.PositiveIntegerField(default=0)
    total_points_earned = models.PositiveIntegerField(default=0)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='bronze')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_level(self):
        if self.total_points_earned >= 5000:
            self.level = 'platinum'
        elif self.total_points_earned >= 2000:
            self.level = 'gold'
        elif self.total_points_earned >= 500:
            self.level = 'silver'
        else:
            self.level = 'bronze'
        self.save()

    @classmethod
    def add_points_for_order(cls, order):
        s = settings
        account, _ = cls.objects.get_or_create(user=order.user)
        points = int(float(order.total) * s.LOYALTY_POINTS_PER_FCFA)
        account.points += points
        account.total_points_earned += points
        account.update_level()
        LoyaltyTransaction.objects.create(
            account=account,
            points=points,
            transaction_type='earn',
            description=f'Commande {order.reference}',
        )

    def redeem_points(self, points):
        if points > self.points:
            raise ValueError('Points insuffisants')
        discount = points * settings.LOYALTY_POINT_VALUE_FCFA
        self.points -= points
        self.save()
        LoyaltyTransaction.objects.create(
            account=self,
            points=-points,
            transaction_type='redeem',
            description=f'Échange contre {discount} FCFA de réduction',
        )
        return discount

    def __str__(self):
        return f'{self.user} — {self.points} pts ({self.level})'

    class Meta:
        verbose_name = 'Compte fidélité'
        verbose_name_plural = 'Comptes fidélité'


class LoyaltyTransaction(models.Model):
    TYPE_CHOICES = [
        ('earn', 'Gagné'),
        ('redeem', 'Échangé'),
        ('expire', 'Expiré'),
        ('bonus', 'Bonus'),
    ]

    account = models.ForeignKey(
        LoyaltyAccount, on_delete=models.CASCADE, related_name='transactions'
    )
    points = models.IntegerField()
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Transaction fidélité'
        verbose_name_plural = 'Transactions fidélité'

    def __str__(self):
        return f'{self.account.user} — {self.points:+d} pts — {self.description}'
