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
    api_key = forms.CharField(widget=forms.PasswordInput)
    api_secret = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = ExchangeAccount
        fields = ['name', 'api_key', 'api_secret', 'strategy']