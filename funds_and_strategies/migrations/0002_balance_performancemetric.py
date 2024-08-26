# Generated by Django 5.0.6 on 2024-06-20 14:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('funds_and_strategies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Balance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, max_digits=20)),
                ('date', models.DateField()),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asset_balances', to='funds_and_strategies.asset')),
            ],
            options={
                'unique_together': {('asset', 'date')},
            },
        ),
        migrations.CreateModel(
            name='PerformanceMetric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('metric_name', models.CharField(max_length=255)),
                ('value', models.DecimalField(decimal_places=2, max_digits=20)),
                ('version', models.IntegerField(default=1)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='funds_and_strategies.asset')),
            ],
            options={
                'unique_together': {('asset', 'date', 'metric_name', 'version')},
            },
        ),
    ]