# Generated by Django 5.0.6 on 2024-07-17 10:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('funds_and_strategies', '0019_remove_balance_modified_by_user_strategy_manual'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='asset',
            options={'ordering': ['date']},
        ),
        migrations.AlterModelOptions(
            name='balance',
            options={'ordering': ['date']},
        ),
        migrations.AlterModelOptions(
            name='performancemetric',
            options={'ordering': ['date']},
        ),
        migrations.AlterModelOptions(
            name='transaction',
            options={'ordering': ['date']},
        ),
    ]