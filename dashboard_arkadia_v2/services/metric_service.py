import logging
from datetime import timedelta
from django.utils import timezone
from funds_and_strategies.models import Strategy, Balance, PerformanceMetric, Transaction
from django.db.models import Sum
from decimal import Decimal

# Configura il logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricService:
    def calculate_daily_performance(self, strategy, balance_date):
        try:
            # Ottieni i bilanci del giorno corrente e del giorno precedente
            current_balance = Balance.objects.filter(strategy=strategy, date=balance_date).first()
            previous_balance_date = balance_date - timedelta(days=1)
            previous_balance = Balance.objects.filter(strategy=strategy, date=previous_balance_date).first()

            # Ottieni i depositi e i prelievi tra le due date
            deposits = Transaction.objects.filter(strategy=strategy, date__gt=previous_balance_date, date__lte=balance_date, type='deposit').aggregate(total_deposits=Sum('value_usd'))['total_deposits'] or Decimal('0.0')
            withdrawals = Transaction.objects.filter(strategy=strategy, date__gt=previous_balance_date, date__lte=balance_date, type='withdrawal').aggregate(total_withdrawals=Sum('value_usd'))['total_withdrawals'] or Decimal('0.0')

            # Calcola la performance giornaliera
            if previous_balance and current_balance and previous_balance.value_usd > Decimal('0.0'):
                adjusted_previous_value = Decimal(previous_balance.value_usd) + deposits - withdrawals
                performance = ((Decimal(current_balance.value_usd) - adjusted_previous_value) / adjusted_previous_value) * Decimal('100.0')
            else:
                performance = Decimal('0.0')

            # Salva la performance giornaliera nel database
            PerformanceMetric.objects.update_or_create(
                strategy=strategy,
                date=balance_date,
                metric_name="daily_performance",
                defaults={'value': performance}
            )
            logger.info(f"Daily performance for {strategy.name} on {balance_date}: {performance}%")
        except Exception as e:
            logger.error(f"Error calculating daily performance for {strategy.name} on {balance_date}: {e}")

    def calculate_cumulative_performance(self, strategy, balance_date):
        try:
            # Ottieni il bilancio iniziale
            initial_balance = Balance.objects.filter(strategy=strategy).order_by('date').first()
            if not initial_balance:
                logger.error(f"No initial balance found for {strategy.name}")
                return
            
            # Ottieni il bilancio corrente
            current_balance = Balance.objects.filter(strategy=strategy, date=balance_date).first()

            # Ottieni i depositi e i prelievi fino alla data corrente
            deposits = Transaction.objects.filter(strategy=strategy, date__lte=balance_date, type='deposit').aggregate(total_deposits=Sum('value_usd'))['total_deposits'] or Decimal('0.0')
            withdrawals = Transaction.objects.filter(strategy=strategy, date__lte=balance_date, type='withdrawal').aggregate(total_withdrawals=Sum('value_usd'))['total_withdrawals'] or Decimal('0.0')

            # Calcola la performance progressiva
            if initial_balance and current_balance and initial_balance.value_usd > Decimal('0.0'):
                adjusted_initial_value = Decimal(initial_balance.value_usd) + deposits - withdrawals
                performance = ((Decimal(current_balance.value_usd) - adjusted_initial_value) / adjusted_initial_value) * Decimal('100.0')
            else:
                performance = Decimal('0.0')

            # Salva la performance progressiva nel database
            PerformanceMetric.objects.update_or_create(
                strategy=strategy,
                date=balance_date,
                metric_name="cumulative_performance",
                defaults={'value': performance}
            )
            logger.info(f"Cumulative performance for {strategy.name} on {balance_date}: {performance}%")
        except Exception as e:
            logger.error(f"Error calculating cumulative performance for {strategy.name} on {balance_date}: {e}")

    def calculate_performances_for_strategy(self, strategy):
        try:
            # Ottieni tutte le date per cui ci sono bilanci per la strategia
            balance_dates = Balance.objects.filter(strategy=strategy).values_list('date', flat=True).distinct()
            for balance_date in balance_dates:
                self.calculate_daily_performance(strategy, balance_date)
                self.calculate_cumulative_performance(strategy, balance_date)
        except Exception as e:
            logger.error(f"Error calculating performances for strategy {strategy.name}: {e}")

    def update_all_performances(self):
        try:
            # Cancella tutte le metriche esistenti
            PerformanceMetric.objects.all().delete()
            logger.info("Deleted all existing performance metrics.")

            # Ottieni tutte le strategie
            strategies = Strategy.objects.all()
            for strategy in strategies:
                self.calculate_performances_for_strategy(strategy)
        except Exception as e:
            logger.error(f"Error updating all performances: {e}")

# Usa questa funzione per avviare il processo di aggiornamento delle performance
def update_all_performances():
    metric_service = MetricService()
    metric_service.update_all_performances()
