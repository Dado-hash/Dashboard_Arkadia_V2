from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet
from django.forms import ValidationError 

class Fund(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

class Strategy(models.Model):
    name = models.CharField(max_length=255)
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE)
    description = models.TextField()
    manual = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Asset(models.Model):
    name = models.CharField(max_length=255)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    exchange_account = models.ForeignKey('ExchangeAccount', null=True, blank=True, on_delete=models.CASCADE)
    wallet = models.ForeignKey('Wallet', null=True, blank=True, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    value_usd = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateField()

    def clean(self):
        if self.exchange_account and self.wallet:
            raise ValidationError('An asset cannot belong to both an exchange account and a wallet.')

class Balance(models.Model):
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    value_usd = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    date = models.DateField()
    last_updated = models.DateTimeField(auto_now=True)

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
    ]
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    asset = models.CharField(max_length=255) 
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    value_usd = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateField()
    strategy = models.ForeignKey(Strategy, null=True, blank=True, on_delete=models.SET_NULL)

class PerformanceMetric(models.Model):
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    date = models.DateField()
    metric_name = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return f"{self.strategy.name} - {self.metric_name} - {self.date}"

class ExchangeAccount(models.Model):
    name = models.CharField(max_length=255)
    exchange = models.CharField(max_length=255)
    _api_key = models.BinaryField()
    _api_secret = models.BinaryField()
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(auto_now=True)
    description = models.TextField()

    def _get_cipher(self):
        return Fernet(settings.SECRET_KEY.encode())

    @property
    def api_key(self):
        return self._get_cipher().decrypt(bytes(self._api_key)).decode()

    @api_key.setter
    def api_key(self, value):
        self._api_key = self._get_cipher().encrypt(value.encode())

    @property
    def api_secret(self):
        return self._get_cipher().decrypt(bytes(self._api_secret)).decode()

    @api_secret.setter
    def api_secret(self, value):
        self._api_secret = self._get_cipher().encrypt(value.encode())

    def __str__(self):
        return self.name

class Wallet(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    network = models.CharField(max_length=255)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    description = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
