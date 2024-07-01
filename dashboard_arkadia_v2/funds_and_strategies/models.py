from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet

settings.SECRET_KEY = 'YOUR_SECRET_KEY_HERE' 

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
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateField()

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
    ]
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    strategy = models.ForeignKey(Strategy, null=True, blank=True, on_delete=models.SET_NULL)

class PerformanceMetric(models.Model):
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    date = models.DateField()
    metric_name = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=20, decimal_places=2)
    version = models.IntegerField(default=1)

    class Meta:
        unique_together = ('asset', 'date', 'metric_name', 'version')

class ExchangeAccount(models.Model):
    name = models.CharField(max_length=255)
    _api_key = models.BinaryField()  # Campo per memorizzare l'API key criptata
    _api_secret = models.BinaryField()  # Campo per memorizzare l'API secret criptata
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def _get_cipher(self):
        return Fernet(settings.SECRET_KEY.encode())

    @property
    def api_key(self):
        return self._get_cipher().decrypt(self._api_key).decode()

    @api_key.setter
    def api_key(self, value):
        self._api_key = self._get_cipher().encrypt(value.encode())

    @property
    def api_secret(self):
        return self._get_cipher().decrypt(self._api_secret).decode()

    @api_secret.setter
    def api_secret(self, value):
        self._api_secret = self._get_cipher().encrypt(value.encode())

