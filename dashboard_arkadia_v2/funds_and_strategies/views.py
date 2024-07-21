from datetime import datetime, timedelta
import json
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.contrib import messages
import requests
from django.db import models
from services.update_assets import update_all_assets
from .models import Asset, Balance, Fund, PerformanceMetric, Strategy, Transaction
from .forms import AssetFormSet, ExchangeAccountForm, FundForm, StrategyForm, TransactionFormSet, WalletForm

# Create your views here.

def get_bitcoin_data():
    # Calcola le date per l'ultimo anno
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    # Convertili in timestamp UNIX
    end_date_unix = int(end_date.timestamp())
    start_date_unix = int(start_date.timestamp())

    # URL dell'API CoinGecko
    url = f'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range?vs_currency=usd&from={start_date_unix}&to={end_date_unix}'
    
    response = requests.get(url)
    data = response.json()
    prices = data['prices']
    labels = [datetime.fromtimestamp(item[0] / 1000).strftime('%Y-%m-%d') for item in prices]
    prices = [item[1] for item in prices]
    
    return labels, prices

def dashboard_view(request):
    labels, data = get_bitcoin_data()
    context = {
        'labels': json.dumps(labels),
        'data': json.dumps(data)
    }
    return render(request, 'funds_and_strategies/dashboard.html', context)

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

def funds(request):
    funds = Fund.objects.all()
    funds_data = []

    for fund in funds:
        balance_data = Balance.objects.filter(fund=fund).order_by('date')
        daily_performance_data = PerformanceMetric.objects.filter(fund=fund, metric_name='daily_performance').order_by('date')
        monthly_performance_data = PerformanceMetric.objects.filter(fund=fund, metric_name='monthly_performance').order_by('date')
        cumulative_performance_data = PerformanceMetric.objects.filter(fund=fund, metric_name='cumulative_performance').order_by('date')
        
        fund_data = {
            'id': fund.id,
            'name': fund.name,
            'balance_labels': [item.date.strftime('%Y-%m-%d') for item in balance_data],
            'balance_values': [float(item.value_usd) for item in balance_data], 
            'daily_labels': [item.date.strftime('%Y-%m-%d') for item in daily_performance_data],
            'daily_values': [float(item.value) for item in daily_performance_data], 
            'monthly_labels': [item.date.strftime('%Y-%m') for item in monthly_performance_data],
            'monthly_values': [float(item.value) for item in monthly_performance_data], 
            'cumulative_labels': [item.date.strftime('%Y-%m-%d') for item in cumulative_performance_data],
            'cumulative_values': [float(item.value) for item in cumulative_performance_data],
        }

        funds_data.append(fund_data)

    context = {
        'funds': funds,
        'funds_data': json.dumps(funds_data),  
    }
    return render(request, 'funds_and_strategies/funds.html', context)

def strategies(request, fund_id):
    fund = get_object_or_404(Fund, id=fund_id)
    strategies = Strategy.objects.filter(fund=fund)

    # Prepara i dati per tutte le strategie
    strategies_data = []
    for strategy in strategies:
        balance_data = Balance.objects.filter(strategy=strategy).order_by('date')
        daily_performance_data = PerformanceMetric.objects.filter(strategy=strategy, metric_name='daily_performance').order_by('date')
        monthly_performance_data = PerformanceMetric.objects.filter(strategy=strategy, metric_name='monthly_performance').order_by('date')
        cumulative_performance_data = PerformanceMetric.objects.filter(strategy=strategy, metric_name='cumulative_performance').order_by('date')

        strategy_data = {
            'id': strategy.id,
            'name': strategy.name,
            'balance_labels': [item.date.strftime('%Y-%m-%d') for item in balance_data],
            'balance_values': [float(item.value_usd) for item in balance_data], 
            'daily_labels': [item.date.strftime('%Y-%m-%d') for item in daily_performance_data],
            'daily_values': [float(item.value) for item in daily_performance_data], 
            'monthly_labels': [item.date.strftime('%Y-%m') for item in monthly_performance_data],
            'monthly_values': [float(item.value) for item in monthly_performance_data], 
            'cumulative_labels': [item.date.strftime('%Y-%m-%d') for item in cumulative_performance_data],
            'cumulative_values': [float(item.value) for item in cumulative_performance_data],
        }

        strategies_data.append(strategy_data)

    context = {
        'strategies': strategies,
        'strategies_data': json.dumps(strategies_data), 
    }
    return render(request, 'funds_and_strategies/strategies.html', context)