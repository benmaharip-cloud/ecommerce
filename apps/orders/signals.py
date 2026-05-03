from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order

@receiver(post_save, sender=Order)
def send_order_notification(sender, instance, created, **kwargs):
    from apps.notifications.models import Notification
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer

    if created:
        # Notification nouvelle commande
        notif = Notification.objects.create(
            user=instance.user,
            notification_type='order',
            title='✅ Commande confirmée !',
            message=f'Votre commande {instance.reference} de {instance.total} FCFA a été confirmée.',
            link=f'/commandes/{instance.id}/',
        )
    else:
        # Notification changement de statut
        status_messages = {
            'processing': ('📦 Commande en préparation', 'Votre commande est en cours de préparation.'),
            'shipped': ('🚚 Commande expédiée !', 'Votre commande est en route vers vous.'),
            'delivered': ('🎉 Commande livrée !', 'Votre commande a été livrée avec succès.'),
            'cancelled': ('❌ Commande annulée', 'Votre commande a été annulée.'),
        }
        if instance.status in status_messages:
            title, message = status_messages[instance.status]
            notif = Notification.objects.create(
                user=instance.user,
                notification_type='order',
                title=title,
                message=message,
                link=f'/commandes/{instance.id}/',
            )
        else:
            return

    # Envoyer via WebSocket
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notifications_{instance.user.id}',
            {
                'type': 'send_notification',
                'title': notif.title,
                'message': notif.message,
                'notification_type': notif.notification_type,
                'link': notif.link,
            }
        )
    except Exception as e:
        print(f'WebSocket erreur: {e}')
