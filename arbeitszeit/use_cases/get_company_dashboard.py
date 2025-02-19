from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID

from arbeitszeit.repositories import (
    CompanyRepository,
    CompanyWorkerRepository,
    PlanRepository,
)


@dataclass
class GetCompanyDashboardUseCase:
    class Failure(Exception):
        pass

    @dataclass
    class Response:
        @dataclass
        class LatestPlansDetails:
            plan_id: UUID
            prd_name: str
            activation_date: datetime

        @dataclass
        class CompanyInfo:
            id: UUID
            name: str
            email: str

        company_info: CompanyInfo
        has_workers: bool
        three_latest_plans: List[LatestPlansDetails]

    company_repository: CompanyRepository
    company_worker_repository: CompanyWorkerRepository
    plan_repository: PlanRepository

    def get_dashboard(self, company_id: UUID) -> Response:
        company = self.company_repository.get_by_id(company_id)
        if company is None:
            raise self.Failure()
        company_info = self.Response.CompanyInfo(
            id=company.id, name=company.name, email=company.email
        )
        has_workers = bool(
            len(list(self.company_worker_repository.get_company_workers(company)))
        )
        three_latest_plans = self._get_three_latest_plans()
        return self.Response(
            company_info=company_info,
            has_workers=has_workers,
            three_latest_plans=three_latest_plans,
        )

    def _get_three_latest_plans(self) -> List[Response.LatestPlansDetails]:
        latest_plans = (
            self.plan_repository.get_three_latest_active_plans_ordered_by_activation_date()
        )
        plans = []
        for plan in latest_plans:
            assert plan.activation_date
            plans.append(
                self.Response.LatestPlansDetails(
                    plan.id, plan.prd_name, plan.activation_date
                )
            )
        return plans
