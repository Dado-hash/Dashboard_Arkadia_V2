from datetime import date
from django.utils import timezone
from funds_and_strategies.models import Asset, Balance, Strategy
from django.db.models import Sum
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BalanceService:
    def calculate_strategy_balance_for_date(self, strategy, balance_date):
        try:
            # Calculate the total value in USD of all assets for the given strategy and date
            total_value_usd = Asset.objects.filter(strategy=strategy, date=balance_date).aggregate(total_value=Sum('value_usd'))['total_value'] or 0.0
            
            # Check if a balance entry already exists for the given date
            balance, created = Balance.objects.get_or_create(strategy=strategy, date=balance_date)
            
            # Ensure that total_value_usd is a float and not None
            if total_value_usd is None:
                total_value_usd = 0.0

            # Assign the calculated value to the balance object
            balance.value_usd = total_value_usd
            balance.last_updated = timezone.now()

            # Save the balance object to the database
            balance.save()
            return balance
        except Exception as e:
            logger.error(f"Error calculating balance for {strategy.name} on {balance_date}: {e}")

    def calculate_balances_for_strategy(self, strategy):
        try:
            # Get all unique dates for which there are assets for the given strategy
            asset_dates = Asset.objects.filter(strategy=strategy).values_list('date', flat=True).distinct()
            for balance_date in asset_dates:
                self.calculate_strategy_balance_for_date(strategy, balance_date)
        except Exception as e:
            logger.error(f"Error calculating balances for strategy {strategy.name}: {e}")

    def update_all_balances(self):
        try:
            # Get all strategies
            strategies = Strategy.objects.all()
            for strategy in strategies:
                self.calculate_balances_for_strategy(strategy)
        except Exception as e:
            logger.error(f"Error updating all balances: {e}")

# Use this function to trigger the balance update process
def update_all_balances():
    balance_service = BalanceService()
    balance_service.update_all_balances()
