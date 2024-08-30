# Generated by Django 5.0.6 on 2024-07-01 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('funds_and_strategies', '0004_alter_balance_unique_together_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='balance',
            old_name='balance',
            new_name='value_usd',
        ),
        migrations.AddField(
            model_name='asset',
            name='value_usd',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transaction',
            name='asset',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transaction',
            name='value_usd',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=20),
            preserve_default=False,
        ),
    ]