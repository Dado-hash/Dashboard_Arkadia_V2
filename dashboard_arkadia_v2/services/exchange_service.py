# services/exchange_service.py

import base64
import urllib.parse
import requests
from datetime import date
from funds_and_strategies.models import ExchangeAccount, Asset
from cryptography.fernet import Fernet
from dashboard_arkadia_v2 import settings
import hmac
import hashlib
import time
from django.utils import timezone

class ExchangeService:
    KRAKEN_ASSET_MAPPING = {
        'ZEUR': 'EUR',
        'XXBT': 'BTC',
        'XETH': 'ETH',
        'USDT.F': 'USDT',
        'USDC.F': 'USDC',
        'XBT.F': 'BTC',
    }

    def __init__(self, exchange_account: ExchangeAccount, prices: dict):
        self.api_key = exchange_account.api_key
        self.api_secret = exchange_account.api_secret
        self.exchange = exchange_account.name.lower()
        self.prices = prices
        self.exchange_account = exchange_account 
        self.cipher = Fernet(settings.SECRET_KEY.encode())

    def _get_binance_spot_assets(self):
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
                    "amount": float(asset['free']) + float(asset['locked']),
                    "price": self.prices.get(f"{asset['asset']}USDT", 1.0),
                    "value_usd": (float(asset['free']) + float(asset['locked'])) * self.prices.get(f"{asset['asset']}USDT", 1.0),
                    "date": date.today()
                }
                for asset in data['balances']
                if float(asset['free']) > 0 or float(asset['locked']) > 0
            ]
            return assets
        else:
            response.raise_for_status()

    def _get_binance_futures_assets(self):
        base_url = "https://fapi.binance.com"
        endpoint = "/fapi/v2/account"
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
                    "amount": float(asset['walletBalance']),
                    "price": self.prices.get(f"{asset['asset']}USDT", 1.0),
                    "value_usd": float(asset['walletBalance']) * self.prices.get(f"{asset['asset']}USDT", 1.0),
                    "date": date.today()
                }
                for asset in data['assets']
                if float(asset['walletBalance']) > 0
            ]
            return assets
        else:
            response.raise_for_status()

    def _get_kraken_assets(self):
        base_url = "https://api.kraken.com"
        endpoint = "/0/private/Balance"
        nonce = str(int(time.time() * 1000000))
        post_data = {
            'nonce': nonce
        }
        post_data_str = urllib.parse.urlencode(post_data)
        message = endpoint.encode() + hashlib.sha256(nonce.encode() + post_data_str.encode()).digest()
        signature = hmac.new(base64.b64decode(self.api_secret), message, hashlib.sha512)
        headers = {
            'API-Key': self.api_key,
            'API-Sign': base64.b64encode(signature.digest()).decode()
        }
        response = requests.post(base_url + endpoint, headers=headers, data=post_data_str)
        
        if response.status_code == 200:
            data = response.json()
            if data['error']:
                raise Exception(f"Kraken API error: {data['error']}")
            balances = data['result']
            assets = [
                {
                    "name": self.KRAKEN_ASSET_MAPPING.get(asset, asset),
                    "amount": float(balance),
                    "price": self.prices.get(f"{self.KRAKEN_ASSET_MAPPING.get(asset, asset)}USDT", 1.0),
                    "value_usd": float(balance) * self.prices.get(f"{self.KRAKEN_ASSET_MAPPING.get(asset, asset)}USDT", 1.0),
                    "date": date.today()
                }
                for asset, balance in balances.items()
                if float(balance) > 0
            ]
            return assets
        else:
            response.raise_for_status()

    def get_assets(self):
        if self.exchange == 'binance' or self.exchange == 'binance_futures':
            if self.exchange == 'binance':
                return self._get_binance_spot_assets()
            elif self.exchange == 'binance_futures':
                return self._get_binance_futures_assets()
        elif self.exchange == 'kraken':
            return self._get_kraken_assets()
        # Implementare metodi simili per Kraken, Deribit e wallet Bitcoin/Ethereum
        else:
            raise ValueError("Unsupported exchange")

    def save_assets_to_db(self, assets):
        today = date.today()
        # Elimina gli asset esistenti per lo stesso giorno
        Asset.objects.filter(strategy=self.exchange_account.strategy, date=today, exchange_account=self.exchange_account).delete()
        for asset in assets:
            Asset.objects.create(
                name=asset['name'],
                amount=asset['amount'],
                price=asset['price'],
                value_usd=asset['value_usd'],
                strategy=self.exchange_account.strategy,
                date=today,
                exchange_account=self.exchange_account
            )
        # Aggiorna il campo last_updated
        self.exchange_account.last_updated = timezone.now()
        self.exchange_account.save()
