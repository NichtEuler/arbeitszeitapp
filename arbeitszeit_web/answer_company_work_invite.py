from dataclasses import dataclass
from typing import Protocol, Union
from uuid import UUID

from arbeitszeit.use_cases import (
    AnswerCompanyWorkInviteRequest,
    AnswerCompanyWorkInviteResponse,
)

from .malformed_input_data import MalformedInputData
from .notification import Notifier
from .session import Session


class AnswerCompanyWorkInviteForm(Protocol):
    def get_is_accepted_field(self) -> bool:
        ...


@dataclass(frozen=True)
class AnswerCompanyWorkInviteController:
    session: Session

    def import_form_data(
        self, form: AnswerCompanyWorkInviteForm, invite_id: UUID
    ) -> Union[None, MalformedInputData, AnswerCompanyWorkInviteRequest]:
        requesting_user = self.session.get_current_user()
        if requesting_user is not None:
            return AnswerCompanyWorkInviteRequest(
                form.get_is_accepted_field(), invite_id, requesting_user
            )
        else:
            return None


@dataclass
class AnswerCompanyWorkInvitePresenter:
    user_notifier: Notifier

    def present(self, response: AnswerCompanyWorkInviteResponse) -> None:
        if response.is_success:
            if response.is_accepted:
                self.user_notifier.display_info(
                    f'Erfolgreich dem Betrieb "{response.company_name}" beigetreten'
                )
            else:
                self.user_notifier.display_info(
                    f'Einladung zum Betrieb "{response.company_name}" abgelehnt'
                )
        else:
            self.user_notifier.display_warning(
                "Annehmen oder Ablehnen dieser Einladung ist nicht möglich"
            )
