from dataclasses import dataclass
from decimal import Decimal

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.decimal import decimal_sum
from arbeitszeit.entities import ProductionCosts
from arbeitszeit.repositories import PayoutFactorRepository, PlanRepository


@inject
@dataclass
class PayoutFactorService:
    plan_repository: PlanRepository
    datetime_service: DatetimeService
    payout_factor_repository: PayoutFactorRepository

    def calculate_payout_factor(self) -> Decimal:
        # payout factor = (A − ( P o + R o )) / (A + A o)
        productive_plans = (
            self.plan_repository.all_productive_plans_approved_active_and_not_expired()
        )
        public_plans = (
            self.plan_repository.all_public_plans_approved_active_and_not_expired()
        )
        # A o, P o, R o
        public_costs_per_day: ProductionCosts = sum(
            (p.production_costs / p.timeframe for p in public_plans),
            start=ProductionCosts(Decimal(0), Decimal(0), Decimal(0)),
        )
        # A
        sum_of_productive_work_per_day = decimal_sum(
            p.production_costs.labour_cost / p.timeframe for p in productive_plans
        )
        numerator = sum_of_productive_work_per_day - (
            public_costs_per_day.means_cost + public_costs_per_day.resource_cost
        )
        denominator = (
            sum_of_productive_work_per_day + public_costs_per_day.labour_cost
        ) or 1
        # Payout factor
        payout_factor = numerator / denominator
        return Decimal(payout_factor)

    def store_payout_factor(self, payout_factor: Decimal) -> None:
        self.payout_factor_repository.store_payout_factor(
            self.datetime_service.now(), payout_factor
        )
