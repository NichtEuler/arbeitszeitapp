from functools import wraps
from typing import List, Optional

from flask_sqlalchemy import SQLAlchemy
from injector import (
    Binder,
    CallableProvider,
    ClassProvider,
    Injector,
    InstanceProvider,
    Module,
    inject,
    provider,
    singleton,
)

from arbeitszeit import entities
from arbeitszeit import repositories as interfaces
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.mail_service import MailService
from arbeitszeit.token import TokenService
from arbeitszeit.use_cases import CheckForUnreadMessages, GetCompanySummary, ReadMessage
from arbeitszeit_web.check_for_unread_message import (
    CheckForUnreadMessagesController,
    CheckForUnreadMessagesPresenter,
)
from arbeitszeit_web.get_plan_summary import GetPlanSummarySuccessPresenter
from arbeitszeit_web.list_all_cooperations import ListAllCooperationsPresenter
from arbeitszeit_web.list_messages import ListMessagesController, ListMessagesPresenter
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.pay_means_of_production import PayMeansOfProductionPresenter
from arbeitszeit_web.query_companies import QueryCompaniesPresenter
from arbeitszeit_web.query_plans import QueryPlansPresenter
from arbeitszeit_web.read_message import ReadMessageController, ReadMessagePresenter
from arbeitszeit_web.request_cooperation import RequestCooperationController
from arbeitszeit_web.show_my_cooperations import ShowMyCooperationsPresenter
from arbeitszeit_web.show_my_plans import ShowMyPlansPresenter
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import (
    CompanySummaryUrlIndex,
    CoopSummaryUrlIndex,
    MessageUrlIndex,
    PlanSummaryUrlIndex,
)
from arbeitszeit_web.user_action_resolver import (
    UserActionResolver,
    UserActionResolverImpl,
)
from project.database import get_social_accounting
from project.database.repositories import (
    AccountOwnerRepository,
    AccountRepository,
    CompanyRepository,
    CompanyWorkerRepository,
    CooperationRepository,
    MemberRepository,
    MessageRepository,
    PlanCooperationRepository,
    PlanDraftRepository,
    PlanRepository,
    PurchaseRepository,
    TransactionRepository,
    WorkerInviteRepository,
)
from project.datetime import RealtimeDatetimeService
from project.extensions import db
from project.flask_session import FlaskSession
from project.mail_service import get_mail_service
from project.notifications import FlaskFlashNotifier
from project.template import (
    CompanyTemplateIndex,
    FlaskTemplateRenderer,
    MemberTemplateIndex,
    TemplateIndex,
    TemplateRenderer,
    UserTemplateRenderer,
)
from project.token import FlaskTokenService
from project.url_index import CompanyUrlIndex, MemberUrlIndex
from project.views import Http404View, ReadMessageView

from .translator import FlaskTranslator


class MemberModule(Module):
    @provider
    def provide_plan_summary_url_index(
        self, member_index: MemberUrlIndex
    ) -> PlanSummaryUrlIndex:
        return member_index

    @provider
    def provide_coop_summary_url_index(
        self, member_index: MemberUrlIndex
    ) -> CoopSummaryUrlIndex:
        return member_index

    @provider
    def provide_message_url_index(
        self, member_index: MemberUrlIndex
    ) -> MessageUrlIndex:
        return member_index

    @provider
    def provide_company_url_index(
        self, member_index: MemberUrlIndex
    ) -> CompanySummaryUrlIndex:
        return member_index

    @provider
    def provide_template_index(self) -> TemplateIndex:
        return MemberTemplateIndex()


class CompanyModule(Module):
    @provider
    def provide_plan_summary_url_index(
        self, company_index: CompanyUrlIndex
    ) -> PlanSummaryUrlIndex:
        return company_index

    @provider
    def provide_coop_summary_url_index(
        self, company_index: CompanyUrlIndex
    ) -> CoopSummaryUrlIndex:
        return company_index

    @provider
    def provide_message_url_index(
        self, company_index: CompanyUrlIndex
    ) -> MessageUrlIndex:
        return company_index

    @provider
    def provide_company_url_index(
        self, company_index: CompanyUrlIndex
    ) -> CompanySummaryUrlIndex:
        return company_index

    @provider
    def provide_template_index(self) -> TemplateIndex:
        return CompanyTemplateIndex()


class FlaskModule(Module):
    @provider
    def provide_get_company_summary(
        self,
        company_repository: interfaces.CompanyRepository,
        plan_repository: interfaces.PlanRepository,
    ) -> GetCompanySummary:
        return GetCompanySummary(company_repository, plan_repository)

    @provider
    def provide_read_message_view(
        self,
        read_message: ReadMessage,
        controller: ReadMessageController,
        presenter: ReadMessagePresenter,
        template_renderer: TemplateRenderer,
        template_index: TemplateIndex,
        http_404_view: Http404View,
    ) -> ReadMessageView:
        return ReadMessageView(
            read_message,
            controller,
            presenter,
            template_renderer,
            template_index,
            http_404_view,
        )

    @provider
    def provide_http_404_view(
        self, template_renderer: TemplateRenderer, template_index: TemplateIndex
    ) -> Http404View:
        return Http404View(
            template_index=template_index, template_renderer=template_renderer
        )

    @provider
    def provide_query_companies_presenter(
        self, notifier: Notifier
    ) -> QueryCompaniesPresenter:
        return QueryCompaniesPresenter(user_notifier=notifier)

    @provider
    def provide_pay_means_of_production_presenter(
        self, notifier: Notifier
    ) -> PayMeansOfProductionPresenter:
        return PayMeansOfProductionPresenter(notifier)

    @provider
    def provide_list_all_cooperations_presenter(
        self, coop_index: CoopSummaryUrlIndex
    ) -> ListAllCooperationsPresenter:
        return ListAllCooperationsPresenter(coop_index)

    @provider
    def provide_show_my_cooperations_presenter(
        self, coop_index: CoopSummaryUrlIndex
    ) -> ShowMyCooperationsPresenter:
        return ShowMyCooperationsPresenter(coop_index)

    @provider
    def provide_show_my_plans_presenter(
        self, plan_index: PlanSummaryUrlIndex, coop_index: CoopSummaryUrlIndex
    ) -> ShowMyPlansPresenter:
        return ShowMyPlansPresenter(plan_index, coop_index)

    @provider
    def provide_list_messages_presenter(
        self, message_index: MessageUrlIndex
    ) -> ListMessagesPresenter:
        return ListMessagesPresenter(message_index)

    @provider
    def provide_query_plans_presenter(
        self,
        plan_index: PlanSummaryUrlIndex,
        coop_index: CoopSummaryUrlIndex,
        notifier: Notifier,
    ) -> QueryPlansPresenter:
        return QueryPlansPresenter(plan_index, coop_index, user_notifier=notifier)

    @provider
    def provide_user_action_resolver(self) -> UserActionResolver:
        return UserActionResolverImpl()

    @provider
    def provide_get_plan_summary_success_presenter(
        self,
        coop_index: CoopSummaryUrlIndex,
        company_index: CompanySummaryUrlIndex,
        trans: Translator,
    ) -> GetPlanSummarySuccessPresenter:
        return GetPlanSummarySuccessPresenter(coop_index, company_index, trans)

    @provider
    def provide_transaction_repository(
        self, instance: TransactionRepository
    ) -> interfaces.TransactionRepository:
        return instance

    @provider
    def provide_template_renderer(self) -> TemplateRenderer:
        return FlaskTemplateRenderer()

    @provider
    def provide_user_template_renderer(
        self,
        flask_template_renderer: FlaskTemplateRenderer,
        session: FlaskSession,
        check_unread_messages_use_case: CheckForUnreadMessages,
        check_unread_messages_controller: CheckForUnreadMessagesController,
        check_unread_messages_presenter: CheckForUnreadMessagesPresenter,
    ) -> UserTemplateRenderer:
        return UserTemplateRenderer(
            flask_template_renderer,
            session,
            check_unread_messages_use_case,
            check_unread_messages_controller,
            check_unread_messages_presenter,
        )

    @provider
    def provide_list_messages_controller(
        self, session: FlaskSession
    ) -> ListMessagesController:
        return ListMessagesController(session)

    @provider
    def provide_request_cooperation_controller(
        self, session: FlaskSession
    ) -> RequestCooperationController:
        return RequestCooperationController(session)

    @provider
    def provide_read_message_controller(
        self, session: FlaskSession
    ) -> ReadMessageController:
        return ReadMessageController(session)

    @provider
    def provide_read_message_presenter(
        self, user_action_resolver: UserActionResolver
    ) -> ReadMessagePresenter:
        return ReadMessagePresenter(user_action_resolver)

    @provider
    def provide_notifier(self) -> Notifier:
        return FlaskFlashNotifier()

    @singleton
    @provider
    def provide_mail_service(self) -> MailService:
        return get_mail_service()

    @provider
    def provide_translator(self) -> Translator:
        return FlaskTranslator()

    def configure(self, binder: Binder) -> None:
        binder.bind(
            interfaces.CompanyWorkerRepository,  # type: ignore
            to=ClassProvider(CompanyWorkerRepository),
        )
        binder.bind(
            interfaces.PurchaseRepository,  # type: ignore
            to=ClassProvider(PurchaseRepository),
        )
        binder.bind(
            entities.SocialAccounting,
            to=CallableProvider(get_social_accounting),
        )
        binder.bind(
            interfaces.AccountRepository,  # type: ignore
            to=ClassProvider(AccountRepository),
        )
        binder.bind(
            interfaces.MemberRepository,  # type: ignore
            to=ClassProvider(MemberRepository),
        )
        binder.bind(
            interfaces.CompanyRepository,  # type: ignore
            to=ClassProvider(CompanyRepository),
        )
        binder.bind(
            interfaces.PurchaseRepository,  # type: ignore
            to=ClassProvider(PurchaseRepository),
        )
        binder.bind(
            interfaces.PlanRepository,  # type: ignore
            to=ClassProvider(PlanRepository),
        )
        binder.bind(
            interfaces.AccountOwnerRepository,  # type: ignore
            to=ClassProvider(AccountOwnerRepository),
        )
        binder.bind(
            interfaces.PlanDraftRepository,  # type: ignore
            to=ClassProvider(PlanDraftRepository),
        )
        binder.bind(
            DatetimeService,  # type: ignore
            to=ClassProvider(RealtimeDatetimeService),
        )
        binder.bind(
            interfaces.WorkerInviteRepository,  # type: ignore
            to=ClassProvider(WorkerInviteRepository),
        )
        binder.bind(
            SQLAlchemy,
            to=InstanceProvider(db),
        )
        binder.bind(
            interfaces.MessageRepository,  # type: ignore
            to=ClassProvider(MessageRepository),
        )
        binder.bind(
            interfaces.CooperationRepository,  # type: ignore
            to=ClassProvider(CooperationRepository),
        )
        binder.bind(
            interfaces.PlanCooperationRepository,  # type: ignore
            to=ClassProvider(PlanCooperationRepository),
        )
        binder.bind(TokenService, to=ClassProvider(FlaskTokenService))  # type: ignore


class with_injection:
    def __init__(self, modules: Optional[List[Module]] = None) -> None:
        self._modules = modules if modules is not None else []

    def __call__(self, original_function):
        """When you wrap a function, make sure that the parameters to be
        injected come after the the parameters that the caller should
        provide.
        """

        @wraps(original_function)
        def wrapped_function(*args, **kwargs):
            return self.get_injector().call_with_injection(
                inject(original_function), args=args, kwargs=kwargs
            )

        return wrapped_function

    def get_injector(self) -> Injector:
        all_modules: List[Module] = []
        all_modules.append(FlaskModule())
        all_modules += self._modules
        return Injector(all_modules)
