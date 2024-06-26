# Generated by Django 4.2.5 on 2024-06-22 09:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders_app', '0005_alter_order_status'),
        ('restaurants_app', '0003_menuimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='Qrcode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='생성일')),
                ('return_date', models.DateTimeField(auto_now_add=True, verbose_name='반납일자')),
                ('status', models.CharField(default='미반납', max_length=255, verbose_name='상태')),
                ('orderId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders_app.order')),
                ('userId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
