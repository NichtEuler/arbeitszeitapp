from decimal import Decimal
from unittest import TestCase

from arbeitszeit.use_cases.show_my_accounts import ShowMyAccountsResponse
from arbeitszeit_web.presenters.show_my_accounts_presenter import (
    ShowMyAccountsPresenter,
)
from tests.use_cases.dependency_injection import get_dependency_injector


class ShowMyAccountsPresenterTests(TestCase):
    def setUp(self):
        self.injector = get_dependency_injector()
        self.presenter = self.injector.get(ShowMyAccountsPresenter)

    def test_show_correct_balance_string_for_balances(self):
        presentation = self.presenter.present(
            ShowMyAccountsResponse(
                balances=[Decimal(0), Decimal(-1), Decimal(2.0051), Decimal(2.5)]
            )
        )
        self.assertEqual(presentation.balance_fixed, "0.00")
        self.assertEqual(presentation.balance_liquid, "-1.00")
        self.assertEqual(presentation.balance_work, "2.01")
        self.assertEqual(presentation.balance_product, "2.50")

    def test_show_correct_signs_for_balances(self):
        presentation = self.presenter.present(
            ShowMyAccountsResponse(
                balances=[Decimal(0), Decimal(-1), Decimal(2.0051), Decimal(2.5)]
            )
        )
        self.assertEqual(presentation.is_fixed_positive, True)
        self.assertEqual(presentation.is_liquid_positive, False)
        self.assertEqual(presentation.is_work_positive, True)
        self.assertEqual(presentation.is_product_positive, True)
