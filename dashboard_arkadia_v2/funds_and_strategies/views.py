from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages

from services.update_assets import update_all_assets
from .models import Asset, ExchangeAccount, Strategy, Transaction, Wallet
from .forms import AssetFormSet, ExchangeAccountForm, FundForm, StrategyForm, TransactionFormSet, WalletForm

# Create your views here.

def dashboard_view(request):
    return render(request, 'funds_and_strategies/dashboard.html')

def settings(request):
    return render(request, 'funds_and_strategies/settings.html')

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
    return render(request, 'funds_and_strategies/save_strategy.html', {'form': form})

def save_api_keys(request):
    if request.method == 'POST':
        form = ExchangeAccountForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "success", "message": "API keys saved successfully"})
        else:
            return JsonResponse({"status": "error", "message": "Invalid form data"})
    else:
        form = ExchangeAccountForm()
    return render(request, 'funds_and_strategies/save_api_keys.html', {'form': form})

def save_wallet(request):
    if request.method == 'POST':
        form = WalletForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "success", "message": "Wallet saved successfully"})
        else:
            return JsonResponse({"status": "error", "message": "Invalid form data"})
    else:
        form = WalletForm()
    return render(request, 'funds_and_strategies/save_wallet.html', {'form': form})

def update_assets(request):
    try:
        update_all_assets()
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})
    
def add_assets(request):
    if request.method == 'POST':
        formset = AssetFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.value_usd = instance.amount * instance.price
                instance.save()
            messages.success(request, 'Assets added successfully!')
            return redirect('add_assets')
    else:
        formset = AssetFormSet(queryset=Asset.objects.none())

    strategies = Strategy.objects.all()

    return render(request, 'funds_and_strategies/add_assets.html', {
        'formset': formset,
        'strategies': strategies
    })

def add_transactions(request):
    if request.method == 'POST':
        formset = TransactionFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.value_usd = instance.amount * instance.price
                instance.save()
            messages.success(request, 'Transactions added successfully!')
            return redirect('add_transactions')
    else:
        formset = TransactionFormSet(queryset=Transaction.objects.none())

    strategies = Strategy.objects.all()

    return render(request, 'funds_and_strategies/add_transactions.html', {
        'formset': formset,
        'strategies': strategies
    })