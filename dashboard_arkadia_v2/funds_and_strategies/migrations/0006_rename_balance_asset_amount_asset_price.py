# Generated by Django 5.0.6 on 2024-07-03 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('funds_and_strategies', '0005_rename_balance_balance_value_usd_asset_value_usd_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='asset',
            old_name='balance',
            new_name='amount',
        ),
        migrations.AddField(
            model_name='asset',
            name='price',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=20),
            preserve_default=False,
        ),
    ]
