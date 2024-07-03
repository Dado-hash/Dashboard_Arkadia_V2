from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import ExchangeAccount
from .forms import ExchangeAccountForm, FundForm, StrategyForm

# Create your views here.

def index(request):
    return render(request, 'funds_and_strategies/index.html')

def save_fund(request):
    if request.method == 'POST':
        form = FundForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "success", "message": "Fund saved successfully"})
        else:
            return JsonResponse({"status": "error", "message": "Invalid form data"})
    else:
        form = FundForm()
    return render(request, 'funds_and_strategies/save_fund.html', {'form': form})

def save_strategy(request):
    if request.method == 'POST':
        form = StrategyForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "success", "message": "Strategy saved successfully"})
        else:
            return JsonResponse({"status": "error", "message": "Invalid form data"})
    else:
        form = StrategyForm()
    return render(request, 'funds_and_strategies//save_strategy.html', {'form': form})

def save_api_keys(request):
    if request.method == 'POST':
        form = ExchangeAccountForm(request.POST)
        if form.is_valid():
            exchange_account = form.save(commit=False)
            exchange_account.api_key = form.cleaned_data['api_key']
            exchange_account.api_secret = form.cleaned_data['api_secret']
            exchange_account.save()
            return JsonResponse({"status": "success", "message": "API keys saved successfully"})
        else:
            return JsonResponse({"status": "error", "message": "Invalid form data"})
    else:
        form = ExchangeAccountForm()
    return render(request, 'funds_and_strategies/save_api_keys.html', {'form': form})