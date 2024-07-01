# services/exchange_service.py
from datetime import date
import requests
from funds_and_strategies.models import ExchangeAccount, Asset
from cryptography.fernet import Fernet
from dashboard_arkadia_v2 import settings
import hmac
import hashlib
import time

class ExchangeService:
    def __init__(self, exchange_account: ExchangeAccount):
        self.api_key = exchange_account.api_key
        self.api_secret = exchange_account.api_secret
        self.exchange = exchange_account.name.lower()
        self.cipher = Fernet(settings.SECRET_KEY.encode())

    def get_assets(self):
        if self.exchange == 'binance':
            return self._get_binance_assets()
        elif self.exchange == 'kraken':
            return self._get_kraken_assets()
        elif self.exchange == 'deribit':
            return self._get_deribit_assets()
        else:
            raise ValueError("Unsupported exchange")

    def _get_binance_assets(self):
        base_url = "https://api.binance.com"
        endpoint = "/api/v3/account"
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}"
        signature = hmac.new(self.api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()
        headers = {
            "X-MBX-APIKEY": self.api_key
        }
        url = f"{base_url}{endpoint}?{query_string}&signature={signature}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            assets = [
                {
                    "name": asset['asset'],
                    "balance": asset['free']
                }
                for asset in data['balances']
                if float(asset['free']) > 0
            ]
            return assets
        else:
            response.raise_for_status()

    def _get_kraken_assets(self):
        # Implement the Kraken API interaction here
        pass

    def _get_deribit_assets(self):
        # Implement the Deribit API interaction here
        pass

    def save_assets_to_db(self, assets):
        today = date.today()
        for asset in assets:
            Asset.objects.create(
                name=asset['name'],
                balance=asset['balance'],
                strategy=self.exchange_account.strategy,
                date=today  # Aggiungi la data di oggi
            )
