from funds_and_strategies.models import ExchangeAccount
from .price_service import PriceService
from .exchange_service import ExchangeService

def update_all_assets():
    price_service = PriceService()
    prices = price_service.get_prices()

    exchange_accounts = ExchangeAccount.objects.all()
    for account in exchange_accounts:
        exchange_service = ExchangeService(account, prices)
        assets = exchange_service.get_assets()
        exchange_service.save_assets_to_db(assets)

    # Implementare il download e salvataggio per wallet Bitcoin ed Ethereum usando gli stessi prezzi