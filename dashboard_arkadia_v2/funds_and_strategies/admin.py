from django.contrib import admin
from .models import Fund, Strategy, Asset, Balance, Transaction, PerformanceMetric, ExchangeAccount, Wallet

class FundAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

class StrategyAdmin(admin.ModelAdmin):
    list_display = ('name', 'fund', 'manual', 'description')
    search_fields = ('name', 'fund__name')
    list_filter = ('fund',)

class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'strategy', 'exchange_account', 'wallet', 'amount', 'value_usd', 'date')
    search_fields = ('name', 'strategy__name')
    list_filter = ('strategy',)

class BalanceAdmin(admin.ModelAdmin):
    list_display = ('strategy', 'value_usd', 'date')
    search_fields = ('strategy__name',)
    list_filter = ('strategy', 'date')

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('type', 'asset', 'amount', 'value_usd', 'date', 'strategy')
    search_fields = ('type', 'strategy__name')
    list_filter = ('type', 'strategy')

class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ('strategy', 'date', 'metric_name', 'value')
    search_fields = ('strategy__name', 'metric_name')
    list_filter = ('strategy', 'date', 'metric_name')

class ExchangeAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'strategy', 'exchange')
    search_fields = ('name', 'strategy__name')
    list_filter = ('strategy',)

class WalletAdmin(admin.ModelAdmin):
    list_display = ('name', 'strategy', 'address', 'network', 'description', 'last_updated')
    search_fields = ('name', 'strategy__name')
    list_filter = ('strategy',)

admin.site.register(Fund, FundAdmin)
admin.site.register(Strategy, StrategyAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(Balance, BalanceAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(PerformanceMetric, PerformanceMetricAdmin)
admin.site.register(ExchangeAccount, ExchangeAccountAdmin)
admin.site.register(Wallet, WalletAdmin)
