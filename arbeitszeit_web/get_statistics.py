from dataclasses import dataclass
from typing import Optional

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import PayoutFactor
from arbeitszeit.use_cases import StatisticsResponse
from arbeitszeit_web.colors import Colors
from arbeitszeit_web.plotter import Plotter
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class GetStatisticsViewModel:
    registered_companies_count: str
    registered_members_count: str
    cooperations_count: str
    certificates_count: str
    available_product: str
    active_plans_count: str
    active_plans_public_count: str
    average_timeframe_days: str
    planned_work_hours: str
    planned_resources_hours: str
    planned_means_hours: str
    payout_factor: str
    payout_factor_explanation: str

    barplot_for_certificates_url: str
    barplot_means_of_production_url: str
    barplot_plans_url: str


@inject
@dataclass
class GetStatisticsPresenter:
    translator: Translator
    plotter: Plotter
    colors: Colors
    url_index: UrlIndex
    datetime_service: DatetimeService

    def present(self, use_case_response: StatisticsResponse) -> GetStatisticsViewModel:
        average_timeframe = self.translator.gettext("%(num).2f days") % dict(
            num=use_case_response.avg_timeframe
        )
        planned_work = self.translator.gettext("%(num).2f hours") % dict(
            num=use_case_response.planned_work
        )
        planned_liquid_means = self.translator.gettext("%(num).2f hours") % dict(
            num=use_case_response.planned_resources
        )
        planned_fixed_means = self.translator.gettext("%(num).2f hours") % dict(
            num=use_case_response.planned_means
        )
        return GetStatisticsViewModel(
            planned_resources_hours=planned_liquid_means,
            planned_work_hours=planned_work,
            planned_means_hours=planned_fixed_means,
            registered_companies_count=str(
                use_case_response.registered_companies_count
            ),
            registered_members_count=str(use_case_response.registered_members_count),
            cooperations_count=str(use_case_response.cooperations_count),
            certificates_count="%(num).2f"
            % dict(num=use_case_response.certificates_count),
            available_product="%(num).2f"
            % dict(num=use_case_response.available_product),
            active_plans_count=str(use_case_response.active_plans_count),
            active_plans_public_count=str(use_case_response.active_plans_public_count),
            average_timeframe_days=average_timeframe,
            payout_factor=self._format_payout_factor(use_case_response.payout_factor),
            payout_factor_explanation=self._format_payout_factor_explanation(
                use_case_response.payout_factor
            ),
            barplot_for_certificates_url=self.url_index.get_global_barplot_for_certificates_url(
                use_case_response.certificates_count,
                use_case_response.available_product,
            ),
            barplot_means_of_production_url=self.url_index.get_global_barplot_for_means_of_production_url(
                use_case_response.planned_means,
                use_case_response.planned_resources,
                use_case_response.planned_work,
            ),
            barplot_plans_url=self.url_index.get_global_barplot_for_plans_url(
                (
                    use_case_response.active_plans_count
                    - use_case_response.active_plans_public_count
                ),
                use_case_response.active_plans_public_count,
            ),
        )

    def _format_payout_factor(self, payout_factor: Optional[PayoutFactor]) -> str:
        if payout_factor is None:
            return self.translator.gettext("Not found.")
        return round(payout_factor.value, 2).__str__()

    def _format_payout_factor_explanation(
        self, payout_factor: Optional[PayoutFactor]
    ) -> str:
        if payout_factor is None:
            return self.translator.gettext("Not found.")
        timestamp = self.datetime_service.format_datetime(
            payout_factor.calculation_date, zone="Europe/Berlin", fmt="%d.%m.%Y %H:%M"
        )
        return self.translator.gettext("Payout factor (%(timestamp)s)") % dict(
            timestamp=timestamp
        )
