from django.contrib import admin
from .models import Fund, Strategy, Asset, Balance, Transaction, PerformanceMetric, ExchangeAccount

class FundAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

class StrategyAdmin(admin.ModelAdmin):
    list_display = ('name', 'fund', 'description')
    search_fields = ('name', 'fund__name')
    list_filter = ('fund',)

class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'strategy', 'balance', 'date')
    search_fields = ('name', 'strategy__name')
    list_filter = ('strategy',)

class BalanceAdmin(admin.ModelAdmin):
    list_display = ('strategy', 'balance', 'date')
    search_fields = ('strategy__name',)
    list_filter = ('strategy', 'date')

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('type', 'amount', 'date', 'strategy')
    search_fields = ('type', 'strategy__name')
    list_filter = ('type', 'strategy')

class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ('strategy', 'date', 'metric_name', 'value')
    search_fields = ('strategy__name', 'metric_name')
    list_filter = ('strategy', 'date', 'metric_name')

class ExchangeAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'strategy', 'date_added')
    search_fields = ('name', 'strategy__name')
    list_filter = ('strategy',)

# Registra i modelli con le classi personalizzate
admin.site.register(Fund, FundAdmin)
admin.site.register(Strategy, StrategyAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(Balance, BalanceAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(PerformanceMetric, PerformanceMetricAdmin)
admin.site.register(ExchangeAccount, ExchangeAccountAdmin)
