from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional, Protocol, Tuple

from arbeitszeit.plan_summary import BusinessPlanSummary
from arbeitszeit_web.url_index import CompanySummaryUrlIndex, CoopSummaryUrlIndex

from .translator import Translator


@dataclass
class PlanSummary:
    plan_id: Tuple[str, str]
    is_active: Tuple[str, str]
    planner: Tuple[str, str, str, str]
    product_name: Tuple[str, str]
    description: Tuple[str, List[str]]
    timeframe: Tuple[str, str]
    production_unit: Tuple[str, str]
    amount: Tuple[str, str]
    means_cost: Tuple[str, str]
    resources_cost: Tuple[str, str]
    labour_cost: Tuple[str, str]
    type_of_plan: Tuple[str, str]
    price_per_unit: Tuple[str, str, bool, Optional[str]]
    is_available: Tuple[str, str]


class PlanSummaryService(Protocol):
    def get_plan_summary(self, plan_summary: BusinessPlanSummary) -> PlanSummary:
        ...


@dataclass
class PlanSummaryServiceImpl:
    coop_url_index: CoopSummaryUrlIndex
    company_url_index: CompanySummaryUrlIndex
    translator: Translator

    def get_plan_summary(self, plan_summary: BusinessPlanSummary) -> PlanSummary:
        return PlanSummary(
            plan_id=(self.translator.gettext("Plan ID"), str(plan_summary.plan_id)),
            is_active=(
                self.translator.gettext("Status"),
                self.translator.gettext("Active")
                if plan_summary.is_active
                else self.translator.gettext("Inactive"),
            ),
            planner=(
                self.translator.gettext("Planning company"),
                str(plan_summary.planner_id),
                self.company_url_index.get_company_summary_url(plan_summary.planner_id),
                plan_summary.planner_name,
            ),
            product_name=(
                self.translator.gettext("Name of product"),
                plan_summary.product_name,
            ),
            description=(
                self.translator.gettext("Description of product"),
                plan_summary.description.splitlines(),
            ),
            timeframe=(
                self.translator.gettext("Planning timeframe (days)"),
                str(plan_summary.timeframe),
            ),
            production_unit=(
                self.translator.gettext("Smallest delivery unit"),
                plan_summary.production_unit,
            ),
            amount=(self.translator.gettext("Amount"), str(plan_summary.amount)),
            means_cost=(
                self.translator.gettext("Costs for fixed means of production"),
                str(plan_summary.means_cost),
            ),
            resources_cost=(
                self.translator.gettext("Costs for liquid means of production"),
                str(plan_summary.resources_cost),
            ),
            labour_cost=(
                self.translator.gettext("Costs for work"),
                str(plan_summary.labour_cost),
            ),
            type_of_plan=(
                self.translator.gettext("Type"),
                self.translator.gettext("Public")
                if plan_summary.is_public_service
                else self.translator.gettext("Productive"),
            ),
            price_per_unit=(
                self.translator.gettext("Price (per unit)"),
                self._format_price(plan_summary.price_per_unit),
                plan_summary.is_cooperating,
                self.coop_url_index.get_coop_summary_url(plan_summary.cooperation)
                if plan_summary.cooperation
                else None,
            ),
            is_available=(
                self.translator.gettext("Product currently available"),
                self.translator.gettext("Yes")
                if plan_summary.is_available
                else self.translator.gettext("No"),
            ),
        )

    def _format_price(self, price_per_unit: Decimal) -> str:
        return f"{round(price_per_unit, 2)}"
