# Generated by Django 5.0.6 on 2024-08-21 16:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('funds_and_strategies', '0024_delete_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='fund',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='funds_and_strategies.fund'),
        ),
    ]