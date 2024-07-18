from django.contrib import admin
from .models import Fund, Strategy, Asset, Balance, Transaction, PerformanceMetric, ExchangeAccount, Wallet

class FundAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

class StrategyAdmin(admin.ModelAdmin):
    list_display = ('name', 'fund', 'manual', 'description')
    search_fields = ('name', 'fund__name')
    list_filter = ('fund',)
    ordering = ('name',)

class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'strategy', 'exchange_account', 'wallet', 'amount', 'value_usd', 'date')
    search_fields = ('name', 'strategy__name')
    list_filter = ('strategy', 'date')
    ordering = ('date',)

class BalanceAdmin(admin.ModelAdmin):
    list_display = ('strategy', 'fund', 'value_usd', 'date')
    search_fields = ('strategy__name',)
    list_filter = ('strategy', 'date')
    ordering = ('date',)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('type', 'asset', 'amount', 'value_usd', 'date', 'strategy')
    search_fields = ('type', 'strategy__name')
    list_filter = ('type', 'strategy', 'date')
    ordering = ('date',)

class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ('strategy_or_fund', 'date', 'metric_name', 'value')
    search_fields = ('strategy__name', 'fund__name', 'metric_name')
    list_filter = ('strategy', 'fund', 'date', 'metric_name')
    ordering = ('date',)

class ExchangeAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'strategy', 'exchange')
    search_fields = ('name', 'strategy__name')
    list_filter = ('strategy',)
    ordering = ('name',)

class WalletAdmin(admin.ModelAdmin):
    list_display = ('name', 'strategy', 'address', 'network', 'description', 'last_updated')
    search_fields = ('name', 'strategy__name')
    list_filter = ('strategy',)
    ordering = ('name',)

admin.site.register(Fund, FundAdmin)
admin.site.register(Strategy, StrategyAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(Balance, BalanceAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(PerformanceMetric, PerformanceMetricAdmin)
admin.site.register(ExchangeAccount, ExchangeAccountAdmin)
admin.site.register(Wallet, WalletAdmin)
