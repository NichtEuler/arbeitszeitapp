from decimal import Decimal
from typing import Optional
from uuid import UUID

from arbeitszeit_web.session import UserRole


class CompanyUrlIndexImpl:
    def get_company_dashboard_url(self) -> str:
        return "company dashboard url"


class UrlIndexTestImpl:
    def get_company_plan_summary_url(self, plan_id: UUID) -> str:
        return f"fake_plan_url for company:{plan_id}"

    def get_member_plan_summary_url(self, plan_id: UUID) -> str:
        return f"fake_plan_url for member:{plan_id}"

    def get_member_dashboard_url(self) -> str:
        return "member dashboard url"

    def get_work_invite_url(self, invite_id: UUID) -> str:
        return f"invite url for {invite_id}"

    def get_company_summary_url(
        self, user_role: Optional[UserRole], company_id: UUID
    ) -> str:
        return f"company summary url for: {company_id}, {user_role}"

    def get_coop_summary_url(self, user_role: Optional[UserRole], coop_id: UUID) -> str:
        return f"coop summary url for: {coop_id}, {user_role}"


class RequestCoopUrlIndexTestImpl:
    def get_request_coop_url(self) -> str:
        return "fake_request_coop_url"


class EndCoopUrlIndexTestImpl:
    def get_end_coop_url(self, plan_id: UUID, cooperation_id: UUID) -> str:
        return f"fake_end_coop_url:{plan_id}, {cooperation_id}"


class TogglePlanAvailabilityUrlIndex:
    def get_toggle_availability_url(self, plan_id: UUID) -> str:
        return f"fake_toggle_url:{plan_id}"


class AnswerCompanyWorkInviteUrlIndexImpl:
    def get_answer_company_work_invite_url(self, invite_id: UUID) -> str:
        return f"{invite_id} url"


class RenewPlanUrlIndexTestImpl:
    def get_renew_plan_url(self, plan_id: UUID) -> str:
        return f"fake_renew_url:{plan_id}"


class HidePlanUrlIndexTestImpl:
    def get_hide_plan_url(self, plan_id: UUID) -> str:
        return f"fake_hide_plan_url:{plan_id}"


class ConfirmationUrlIndexImpl:
    def get_confirmation_url(self, token: str) -> str:
        return f"{token} url"


class AccountantInvitationUrlIndexImpl:
    def get_accountant_invitation_url(self, token: str) -> str:
        return f"accountant invitation {token} url"


class PlotsUrlIndexImpl:
    def get_global_barplot_for_certificates_url(
        self, certificates_count: Decimal, available_product: Decimal
    ) -> str:
        return f"barplot url with {certificates_count} and {available_product}"

    def get_global_barplot_for_means_of_production_url(
        self, planned_means: Decimal, planned_resources: Decimal, planned_work: Decimal
    ) -> str:
        return (
            f"barplot url with {planned_means}, {planned_resources} and {planned_work}"
        )

    def get_global_barplot_for_plans_url(
        self, productive_plans: int, public_plans: int
    ) -> str:
        return f"barplot url with {productive_plans} and {public_plans}"

    def get_line_plot_of_company_prd_account(self, company_id: UUID) -> str:
        return f"line plot for {company_id}"

    def get_line_plot_of_company_r_account(self, company_id: UUID) -> str:
        return f"line plot for {company_id}"

    def get_line_plot_of_company_p_account(self, company_id: UUID) -> str:
        return f"line plot for {company_id}"

    def get_line_plot_of_company_a_account(self, company_id: UUID) -> str:
        return f"line plot for {company_id}"


class AccountantDashboardUrlIndexImpl:
    def get_accountant_dashboard_url(self) -> str:
        return "accountant dashboard url"


class PayMeansOfProductionUrlIndexImpl:
    def get_pay_means_of_production_url(self) -> str:
        return "pay means of production form url"


class PayConsumerProductUrlIndexImpl:
    def get_pay_consumer_product_url(self, amount: int, plan_id: UUID) -> str:
        return f"pay consumer product url: {amount}, {plan_id}"


class LanguageChangerUrlIndexImpl:
    def get_language_change_url(self, language_code: str) -> str:
        return f"language change url for {language_code}"


class DraftUrlIndexImpl:
    def get_draft_summary_url(self, draft_id: UUID) -> str:
        return f"fake_draft_url:{draft_id}"
