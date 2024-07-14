from funds_and_strategies.models import ExchangeAccount, Wallet
from .price_service import PriceService
from .exchange_service import ExchangeService
from .wallet_service import WalletService

def update_all_assets():
    # Ottieni i prezzi correnti
    price_service = PriceService()
    prices = price_service.get_prices()

    # Aggiorna gli asset degli account degli exchange
    exchange_accounts = ExchangeAccount.objects.all()
    for account in exchange_accounts:
        exchange_service = ExchangeService(account, prices)
        assets = exchange_service.get_assets()
        exchange_service.save_assets_to_db(assets)

    # Aggiorna i bilanci dei wallets
    wallets = Wallet.objects.all()
    for wallet in wallets:
        wallet_service = WalletService(wallet, prices)
        wallet_service.save_assets_to_db()
