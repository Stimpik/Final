# Generated by Django 5.0 on 2023-12-30 15:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbackend', '0005_alter_shop_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='product_info',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ordered_items', to='dbackend.productinfo', verbose_name='Информация о продукте'),
            preserve_default=False,
        ),
    ]
