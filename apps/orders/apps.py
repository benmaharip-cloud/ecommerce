from django.apps import AppConfig

class OrdersConfig(AppConfig):
    def ready(self):
        import apps.orders.signals
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.orders'
    verbose_name = 'Commandes'
