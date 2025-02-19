from __future__ import annotations

import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from injector import inject

from arbeitszeit.entities import Plan
from arbeitszeit.price_calculator import calculate_price
from arbeitszeit.repositories import PlanCooperationRepository, PlanRepository


class PlanFilter(enum.Enum):
    by_plan_id = enum.auto()
    by_product_name = enum.auto()


class PlanSorting(enum.Enum):
    by_activation = enum.auto()
    by_company_name = enum.auto()
    by_price = enum.auto()


@dataclass
class PlanQueryResponse:
    results: List[QueriedPlan]


@dataclass
class QueriedPlan:
    plan_id: UUID
    company_name: str
    company_id: UUID
    product_name: str
    description: str
    price_per_unit: Decimal
    is_public_service: bool
    is_available: bool
    is_cooperating: bool
    activation_date: datetime


class QueryPlansRequest(ABC):
    @abstractmethod
    def get_query_string(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_filter_category(self) -> PlanFilter:
        pass

    @abstractmethod
    def get_sorting_category(self) -> PlanSorting:
        pass


@inject
@dataclass
class QueryPlans:
    plan_repository: PlanRepository
    plan_cooperation_repository: PlanCooperationRepository

    def __call__(self, request: QueryPlansRequest) -> PlanQueryResponse:
        query = request.get_query_string()
        filter_by = request.get_filter_category()
        sort_by = request.get_sorting_category()
        if query is None:
            found_plans = self.plan_repository.get_active_plans()
        elif filter_by == PlanFilter.by_plan_id:
            found_plans = self.plan_repository.query_active_plans_by_plan_id(query)
        else:
            found_plans = self.plan_repository.query_active_plans_by_product_name(query)
        results = [self._plan_to_response_model(plan) for plan in found_plans]
        results_sorted = self._sort_plans(results, sort_by)
        return PlanQueryResponse(
            results=results_sorted,
        )

    def _plan_to_response_model(self, plan: Plan) -> QueriedPlan:
        price_per_unit = calculate_price(
            self.plan_cooperation_repository.get_cooperating_plans(plan.id)
        )
        assert plan.activation_date
        return QueriedPlan(
            plan_id=plan.id,
            company_name=plan.planner.name,
            company_id=plan.planner.id,
            product_name=plan.prd_name,
            description=plan.description,
            price_per_unit=price_per_unit,
            is_public_service=plan.is_public_service,
            is_available=plan.is_available,
            is_cooperating=bool(plan.cooperation),
            activation_date=plan.activation_date,
        )

    def _sort_plans(
        self, plans: List[QueriedPlan], sort_by: PlanSorting
    ) -> List[QueriedPlan]:
        if sort_by == PlanSorting.by_activation:
            plans = sorted(plans, key=lambda x: x.activation_date, reverse=True)
        elif sort_by == PlanSorting.by_price:
            plans = sorted(plans, key=lambda x: x.price_per_unit)
        else:
            plans = sorted(plans, key=lambda x: x.company_name.casefold())
        return plans
