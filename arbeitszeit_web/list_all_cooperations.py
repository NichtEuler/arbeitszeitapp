from dataclasses import dataclass
from typing import List

from injector import inject

from arbeitszeit.use_cases import ListAllCooperationsResponse
from arbeitszeit_web.session import Session
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class ListedCooperation:
    id: str
    name: str
    plan_count: str
    coop_summary_url: str


@dataclass
class ListAllCooperationsViewModel:
    cooperations: List[ListedCooperation]
    show_results: bool


@inject
@dataclass
class ListAllCooperationsPresenter:
    url_index: UrlIndex
    session: Session

    def present(
        self, response: ListAllCooperationsResponse
    ) -> ListAllCooperationsViewModel:
        cooperations = [
            ListedCooperation(
                id=str(coop.id),
                name=coop.name,
                plan_count=str(coop.plan_count),
                coop_summary_url=self.url_index.get_coop_summary_url(
                    user_role=self.session.get_user_role(), coop_id=coop.id
                ),
            )
            for coop in response.cooperations
        ]
        return ListAllCooperationsViewModel(
            cooperations=cooperations, show_results=bool(cooperations)
        )
