from django.db import migrations, models
import django.db.models.deletion
import uuid

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]
    operations = [
        migrations.AddField(
            model_name='user',
            name='referral_code',
            field=models.CharField(max_length=20, unique=True, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='referred_by',
            field=models.ForeignKey('self', null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name='referrals'),
        ),
        migrations.AddField(
            model_name='user',
            name='referral_points',
            field=models.IntegerField(default=0),
        ),
    ]
