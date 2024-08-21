import logging
from datetime import timedelta, datetime, date
from funds_and_strategies.models import Strategy, Balance, PerformanceMetric, Transaction, Fund
from django.db.models import Sum
from decimal import Decimal

# Configura il logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricService:
    def calculate_daily_performance(self, strategy, balance_date):
        try:
            current_balance = Balance.objects.filter(strategy=strategy, date=balance_date).first()
            previous_balance_date = balance_date - timedelta(days=1)
            previous_balance = Balance.objects.filter(strategy=strategy, date=previous_balance_date).first()

            deposits = Transaction.objects.filter(strategy=strategy, date__gt=previous_balance_date, date__lte=balance_date, type='deposit').aggregate(total_deposits=Sum('value_usd'))['total_deposits'] or Decimal('0.0')
            withdrawals = Transaction.objects.filter(strategy=strategy, date__gt=previous_balance_date, date__lte=balance_date, type='withdrawal').aggregate(total_withdrawals=Sum('value_usd'))['total_withdrawals'] or Decimal('0.0')

            if previous_balance and current_balance and previous_balance.value_usd > Decimal('0.0'):
                adjusted_previous_value = Decimal(previous_balance.value_usd) + deposits - withdrawals
                performance = ((Decimal(current_balance.value_usd) - adjusted_previous_value) / adjusted_previous_value) * Decimal('100.0')
            else:
                performance = Decimal('0.0')

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
            initial_balance = Balance.objects.filter(strategy=strategy).order_by('date').first()
            if not initial_balance:
                logger.error(f"No initial balance found for {strategy.name}")
                return

            current_balance = Balance.objects.filter(strategy=strategy, date=balance_date).first()

            deposits = Transaction.objects.filter(strategy=strategy, date__lte=balance_date, type='deposit').aggregate(total_deposits=Sum('value_usd'))['total_deposits'] or Decimal('0.0')
            withdrawals = Transaction.objects.filter(strategy=strategy, date__lte=balance_date, type='withdrawal').aggregate(total_withdrawals=Sum('value_usd'))['total_withdrawals'] or Decimal('0.0')

            if initial_balance and current_balance and initial_balance.value_usd > Decimal('0.0'):
                adjusted_initial_value = Decimal(initial_balance.value_usd) + deposits - withdrawals
                performance = ((Decimal(current_balance.value_usd) - adjusted_initial_value) / adjusted_initial_value) * Decimal('100.0')
            else:
                performance = Decimal('0.0')

            PerformanceMetric.objects.update_or_create(
                strategy=strategy,
                date=balance_date,
                metric_name="cumulative_performance",
                defaults={'value': performance}
            )
            logger.info(f"Cumulative performance for {strategy.name} on {balance_date}: {performance}%")
        except Exception as e:
            logger.error(f"Error calculating cumulative performance for {strategy.name} on {balance_date}: {e}")

    def get_last_tuesday(self, reference_date):
        last_tuesday = reference_date - timedelta(days=(reference_date.weekday() - 1) % 7)
        return last_tuesday
    
    def calculate_weekly_performance(self, strategy):
        try:
            balance_dates = Balance.objects.filter(strategy=strategy).values_list('date', flat=True).distinct().order_by('date')
            if not balance_dates:
                return

            tuesdays = [self.get_last_tuesday(date) for date in balance_dates if self.get_last_tuesday(date) == date]

            last_tuesday = self.get_last_tuesday(date.today())
            if last_tuesday not in tuesdays and last_tuesday > tuesdays[-1]:
                tuesdays.append(last_tuesday)

            for i in range(len(tuesdays) - 1):
                start_date = tuesdays[i]
                end_date = tuesdays[i + 1]

                start_balance = Balance.objects.filter(strategy=strategy, date=start_date).first()
                end_balance = Balance.objects.filter(strategy=strategy, date=end_date).first()

                if start_balance and end_balance and start_balance.value_usd > Decimal('0.0'):
                    deposits = Transaction.objects.filter(strategy=strategy, date__gt=start_date, date__lte=end_date, type='deposit').aggregate(total_deposits=Sum('value_usd'))['total_deposits'] or Decimal('0.0')
                    withdrawals = Transaction.objects.filter(strategy=strategy, date__gt=start_date, date__lte=end_date, type='withdrawal').aggregate(total_withdrawals=Sum('value_usd'))['total_withdrawals'] or Decimal('0.0')

                    adjusted_start_value = Decimal(start_balance.value_usd) + deposits - withdrawals
                    weekly_performance = ((Decimal(end_balance.value_usd) - adjusted_start_value) / adjusted_start_value) * Decimal('100.0')
                else:
                    weekly_performance = Decimal('0.0')

                PerformanceMetric.objects.update_or_create(
                    strategy=strategy,
                    date=end_date,
                    metric_name="weekly_performance",
                    defaults={'value': weekly_performance}
                )
                logger.info(f"Weekly performance for {strategy.name} from {start_date} to {end_date}: {weekly_performance}%")
        except Exception as e:
            logger.error(f"Error calculating weekly performance for {strategy.name}: {e}")

    def get_last_friday(self, year, month):
        last_day_of_month = datetime(year, month, 1) + timedelta(days=32)
        last_day_of_month = last_day_of_month.replace(day=1) - timedelta(days=1)
        if last_day_of_month.weekday() > 4:
            last_friday = last_day_of_month - timedelta(days=(last_day_of_month.weekday() - 4))
        else:
            last_friday = last_day_of_month
        return last_friday.date()

    def calculate_monthly_performance(self, strategy):
        try:
            balance_dates = Balance.objects.filter(strategy=strategy).values_list('date', flat=True).distinct().order_by('date')
            if not balance_dates:
                return

            monthly_balances = {}
            for date in balance_dates:
                month = date.replace(day=1)
                if month not in monthly_balances:
                    monthly_balances[month] = []
                monthly_balances[month].append(date)

            last_fridays = []
            for year_month in monthly_balances.keys():
                year = year_month.year
                month = year_month.month
                last_friday = self.get_last_friday(year, month)
                last_fridays.append(last_friday)

            today = date.today()
            current_month_last_friday = self.get_last_friday(today.year, today.month)

            if today < current_month_last_friday:
                last_fridays.append(today)
                last_fridays[-2], last_fridays[-1] = last_fridays[-1], last_fridays[-2]
                last_fridays.pop()

            for i in range(len(last_fridays) - 1):
                start_date = last_fridays[i]
                end_date = last_fridays[i + 1]

                start_balance = Balance.objects.filter(strategy=strategy, date=start_date).first()
                end_balance = Balance.objects.filter(strategy=strategy, date=end_date).first()

                if start_balance and end_balance and start_balance.value_usd > Decimal('0.0'):
                    deposits = Transaction.objects.filter(strategy=strategy, date__gt=start_date, date__lte=end_date, type='deposit').aggregate(total_deposits=Sum('value_usd'))['total_deposits'] or Decimal('0.0')
                    withdrawals = Transaction.objects.filter(strategy=strategy, date__gt=start_date, date__lte=end_date, type='withdrawal').aggregate(total_withdrawals=Sum('value_usd'))['total_withdrawals'] or Decimal('0.0')

                    adjusted_start_value = Decimal(start_balance.value_usd) + deposits - withdrawals
                    monthly_performance = ((Decimal(end_balance.value_usd) - adjusted_start_value) / adjusted_start_value) * Decimal('100.0')
                else:
                    monthly_performance = Decimal('0.0')

                PerformanceMetric.objects.update_or_create(
                    strategy=strategy,
                    date=end_date,
                    metric_name="monthly_performance",
                    defaults={'value': monthly_performance}
                )
                logger.info(f"Monthly performance for {strategy.name} on {end_date}: {monthly_performance}%")
        except Exception as e:
            logger.error(f"Error calculating monthly performance for {strategy.name}: {e}")

    def calculate_performances_for_strategy(self, strategy):
        try:
            balance_dates = Balance.objects.filter(strategy=strategy).values_list('date', flat=True).distinct().order_by('date')
            for balance_date in balance_dates:
                self.calculate_daily_performance(strategy, balance_date)
                self.calculate_cumulative_performance(strategy, balance_date)
            self.calculate_weekly_performance(strategy)
            self.calculate_monthly_performance(strategy)
        except Exception as e:
            logger.error(f"Error calculating performances for strategy {strategy.name}: {e}")

    def calculate_daily_performance_for_fund(self, fund, balance_date):
        try:
            current_balance = Balance.objects.filter(fund=fund, date=balance_date).first()
            previous_balance_date = balance_date - timedelta(days=1)
            previous_balance = Balance.objects.filter(fund=fund, date=previous_balance_date).first()

            deposits = Transaction.objects.filter(fund=fund, date__gt=previous_balance_date, date__lte=balance_date, type='deposit').aggregate(total_deposits=Sum('value_usd'))['total_deposits'] or Decimal('0.0')
            withdrawals = Transaction.objects.filter(fund=fund, date__gt=previous_balance_date, date__lte=balance_date, type='withdrawal').aggregate(total_withdrawals=Sum('value_usd'))['total_withdrawals'] or Decimal('0.0')

            if previous_balance and current_balance and previous_balance.value_usd > Decimal('0.0'):
                adjusted_previous_value = Decimal(previous_balance.value_usd) + deposits - withdrawals
                performance = ((Decimal(current_balance.value_usd) - adjusted_previous_value) / adjusted_previous_value) * Decimal('100.0')
            else:
                performance = Decimal('0.0')

            PerformanceMetric.objects.update_or_create(
                fund=fund,
                date=balance_date,
                metric_name="daily_performance",
                defaults={'value': performance}
            )
            logger.info(f"Daily performance for {fund.name} on {balance_date}: {performance}%")
        except Exception as e:
            logger.error(f"Error calculating daily performance for {fund.name} on {balance_date}: {e}")

    def calculate_cumulative_performance_for_fund(self, fund, balance_date):
        try:
            initial_balance = Balance.objects.filter(fund=fund).order_by('date').first()
            if not initial_balance:
                logger.error(f"No initial balance found for {fund.name}")
                return

            current_balance = Balance.objects.filter(fund=fund, date=balance_date).first()

            deposits = Transaction.objects.filter(fund=fund, date__lte=balance_date, type='deposit').aggregate(total_deposits=Sum('value_usd'))['total_deposits'] or Decimal('0.0')
            withdrawals = Transaction.objects.filter(fund=fund, date__lte=balance_date, type='withdrawal').aggregate(total_withdrawals=Sum('value_usd'))['total_withdrawals'] or Decimal('0.0')

            if initial_balance and current_balance and initial_balance.value_usd > Decimal('0.0'):
                adjusted_initial_value = Decimal(initial_balance.value_usd) + deposits - withdrawals
                performance = ((Decimal(current_balance.value_usd) - adjusted_initial_value) / adjusted_initial_value) * Decimal('100.0')
            else:
                performance = Decimal('0.0')

            PerformanceMetric.objects.update_or_create(
                fund=fund,
                date=balance_date,
                metric_name="cumulative_performance",
                defaults={'value': performance}
            )
            logger.info(f"Cumulative performance for {fund.name} on {balance_date}: {performance}%")
        except Exception as e:
            logger.error(f"Error calculating cumulative performance for {fund.name} on {balance_date}: {e}")

    def calculate_weekly_performance_for_fund(self, fund):
        try:
            balance_dates = Balance.objects.filter(fund=fund).values_list('date', flat=True).distinct().order_by('date')
            if not balance_dates:
                return

            tuesdays = [self.get_last_tuesday(date) for date in balance_dates if self.get_last_tuesday(date) == date]

            last_tuesday = self.get_last_tuesday(date.today())
            if last_tuesday not in tuesdays and last_tuesday > tuesdays[-1]:
                tuesdays.append(last_tuesday)

            for i in range(len(tuesdays) - 1):
                start_date = tuesdays[i]
                end_date = tuesdays[i + 1]

                start_balance = Balance.objects.filter(fund=fund, date=start_date).first()
                end_balance = Balance.objects.filter(fund=fund, date=end_date).first()

                if start_balance and end_balance and start_balance.value_usd > Decimal('0.0'):
                    deposits = Transaction.objects.filter(fund=fund, date__gt=start_date, date__lte=end_date, type='deposit').aggregate(total_deposits=Sum('value_usd'))['total_deposits'] or Decimal('0.0')
                    withdrawals = Transaction.objects.filter(fund=fund, date__gt=start_date, date__lte=end_date, type='withdrawal').aggregate(total_withdrawals=Sum('value_usd'))['total_withdrawals'] or Decimal('0.0')

                    adjusted_start_value = Decimal(start_balance.value_usd) + deposits - withdrawals
                    weekly_performance = ((Decimal(end_balance.value_usd) - adjusted_start_value) / adjusted_start_value) * Decimal('100.0')
                else:
                    weekly_performance = Decimal('0.0')

                PerformanceMetric.objects.update_or_create(
                    fund=fund,
                    date=end_date,
                    metric_name="weekly_performance",
                    defaults={'value': weekly_performance}
                )
                logger.info(f"Weekly performance for {fund.name} from {start_date} to {end_date}: {weekly_performance}%")
        except Exception as e:
            logger.error(f"Error calculating weekly performance for {fund.name}: {e}")

    def calculate_monthly_performance_for_fund(self, fund):
        try:
            balance_dates = Balance.objects.filter(fund=fund).values_list('date', flat=True).distinct().order_by('date')
            if not balance_dates:
                return

            monthly_balances = {}
            for date in balance_dates:
                month = date.replace(day=1)
                if month not in monthly_balances:
                    monthly_balances[month] = []
                monthly_balances[month].append(date)

            last_fridays = []
            for year_month in monthly_balances.keys():
                year = year_month.year
                month = year_month.month
                last_friday = self.get_last_friday(year, month)
                last_fridays.append(last_friday)

            today = date.today()
            current_month_last_friday = self.get_last_friday(today.year, today.month)

            if today < current_month_last_friday:
                last_fridays.append(today)
                last_fridays[-2], last_fridays[-1] = last_fridays[-1], last_fridays[-2]
                last_fridays.pop()

            for i in range(len(last_fridays) - 1):
                start_date = last_fridays[i]
                end_date = last_fridays[i + 1]

                start_balance = Balance.objects.filter(fund=fund, date=start_date).first()
                end_balance = Balance.objects.filter(fund=fund, date=end_date).first()

                if start_balance and end_balance and start_balance.value_usd > Decimal('0.0'):
                    deposits = Transaction.objects.filter(fund=fund, date__gt=start_date, date__lte=end_date, type='deposit').aggregate(total_deposits=Sum('value_usd'))['total_deposits'] or Decimal('0.0')
                    withdrawals = Transaction.objects.filter(fund=fund, date__gt=start_date, date__lte=end_date, type='withdrawal').aggregate(total_withdrawals=Sum('value_usd'))['total_withdrawals'] or Decimal('0.0')

                    adjusted_start_value = Decimal(start_balance.value_usd) + deposits - withdrawals
                    monthly_performance = ((Decimal(end_balance.value_usd) - adjusted_start_value) / adjusted_start_value) * Decimal('100.0')
                else:
                    monthly_performance = Decimal('0.0')

                PerformanceMetric.objects.update_or_create(
                    fund=fund,
                    date=end_date,
                    metric_name="monthly_performance",
                    defaults={'value': monthly_performance}
                )
                logger.info(f"Monthly performance for {fund.name} on {end_date}: {monthly_performance}%")
        except Exception as e:
            logger.error(f"Error calculating monthly performance for {fund.name}: {e}")

    def calculate_performances_for_fund(self, fund):
        try:
            balance_dates = Balance.objects.filter(fund=fund).values_list('date', flat=True).distinct().order_by('date')
            for balance_date in balance_dates:
                self.calculate_daily_performance_for_fund(fund, balance_date)
                self.calculate_cumulative_performance_for_fund(fund, balance_date)
            self.calculate_weekly_performance_for_fund(fund)
            self.calculate_monthly_performance_for_fund(fund)
        except Exception as e:
            logger.error(f"Error calculating performances for fund {fund.name}: {e}")

    def update_all_performances(self):
        try:
            PerformanceMetric.objects.all().delete()
            logger.info("Deleted all existing performance metrics.")

            strategies = Strategy.objects.all()
            for strategy in strategies:
                self.calculate_performances_for_strategy(strategy)
            
            funds = Fund.objects.all()
            for fund in funds:
                self.calculate_performances_for_fund(fund)
        except Exception as e:
            logger.error(f"Error updating all performances: {e}")

def update_all_performances():
    metric_service = MetricService()
    metric_service.update_all_performances()
