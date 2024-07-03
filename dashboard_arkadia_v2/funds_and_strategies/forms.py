# forms.py
from django import forms
from .models import ExchangeAccount, Fund, Strategy

class FundForm(forms.ModelForm):
    class Meta:
        model = Fund
        fields = ['name', 'description']

class StrategyForm(forms.ModelForm):
    class Meta:
        model = Strategy
        fields = ['name', 'fund', 'description']

class ExchangeAccountForm(forms.ModelForm):
    EXCHANGE_CHOICES = [
        ('binance', 'Binance'),
        ('binance_futures', 'Binance Futures'),
        ('deribit', 'Deribit'),
        ('kraken', 'Kraken'),
    ]
    
    name = forms.ChoiceField(choices=EXCHANGE_CHOICES)

    api_key = forms.CharField(widget=forms.TextInput, label="API Key")
    api_secret = forms.CharField(widget=forms.PasswordInput, label="API Secret")

    class Meta:
        model = ExchangeAccount
        fields = ['name', 'strategy', 'description']

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.api_key = self.cleaned_data['api_key']
        instance.api_secret = self.cleaned_data['api_secret']
        if commit:
            instance.save()
        return instance