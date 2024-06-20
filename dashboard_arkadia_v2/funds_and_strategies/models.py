from django.db import models

class Fund(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

class Strategy(models.Model):
    name = models.CharField(max_length=255)
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE)
    description = models.TextField()

class Asset(models.Model):
    name = models.CharField(max_length=255)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateField(auto_now_add=True)

class Balance(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='asset_balances')
    balance = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateField()

    class Meta:
        unique_together = ('asset', 'date')

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
    ]
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    strategy = models.ForeignKey(Strategy, null=True, blank=True, on_delete=models.SET_NULL)
    fund = models.ForeignKey(Fund, null=True, blank=True, on_delete=models.SET_NULL)

class PerformanceMetric(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    date = models.DateField()
    metric_name = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=20, decimal_places=2)
    version = models.IntegerField(default=1)

    class Meta:
        unique_together = ('asset', 'date', 'metric_name', 'version')
