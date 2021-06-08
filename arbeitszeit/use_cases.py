from dataclasses import dataclass
from typing import Union
from decimal import Decimal
from enum import Enum

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import (
    Company,
    Member,
    SocialAccounting,
    Plan,
    ProductOffer,
    Purchase,
    Account,
    Transaction,
)
from arbeitszeit.errors import WorkerAlreadyAtCompany
from arbeitszeit.purchase_factory import PurchaseFactory
from arbeitszeit.repositories import (
    CompanyWorkerRepository,
    PurchaseRepository,
    TransactionRepository,
    AccountRepository,
)


class PurposesOfPurchases(Enum):
    means_of_prod = "means_of_prod"
    raw_materials = "raw_materials"


@inject
@dataclass
class PurchaseProduct:
    purchase_repository: PurchaseRepository
    datetime_service: DatetimeService
    purchase_factory: PurchaseFactory

    def __call__(
        self,
        product_offer: ProductOffer,
        amount: int,
        purpose: PurposesOfPurchases,
        buyer: Union[Member, Company],
    ) -> Purchase:
        price = product_offer.price_per_unit
        purchase = self.purchase_factory.create_private_purchase(
            purchase_date=self.datetime_service.now(),
            product_offer=product_offer,
            buyer=buyer,
            price=price,
            amount=amount,
            purpose=purpose,
        )
        assert (
            product_offer.amount_available >= amount
        ), "Amount ordered exceeds available products!"
        product_offer.decrease_amount_available(amount)
        if product_offer.amount_available == amount:
            product_offer.deactivate()

        self.purchase_repository.add(purchase)
        return purchase


def adjust_balance(account: Account, amount: Decimal) -> Account:
    """changes the balance of specified accounts."""
    account.change_credit(amount)
    return account


def register_transaction(
    transaction_repository: TransactionRepository,
    account_from: Account,
    account_to: Account,
    amount: Decimal,
    purpose: str,
) -> Transaction:
    new_transaction = Transaction(account_from, account_to, amount, purpose)
    transaction_repository.add(new_transaction)
    return new_transaction


def add_worker_to_company(
    company_worker_repository: CompanyWorkerRepository,
    company: Company,
    worker: Member,
) -> None:
    """This function may raise a WorkerAlreadyAtCompany exception if the
    worker is already employed at the company."""
    company_workers = company_worker_repository.get_company_workers(company)
    if worker in company_workers:
        raise WorkerAlreadyAtCompany(
            worker=worker,
            company=company,
        )
    company_worker_repository.add_worker_to_company(company, worker)


def approve_plan(
    datetime_service: DatetimeService,
    plan: Plan,
) -> Plan:
    """Company seeks plan approval from Social Accounting."""
    # This is just a place holder
    is_approval = True
    approval_date = datetime_service.now()
    if is_approval:
        plan.approve(approval_date)
    else:
        plan.deny("Some reason", approval_date)
    return plan


def granting_credit(
    plan: Plan,
) -> None:
    """Social Accounting grants credit after plan has been approved."""
    # adjust company balances
    adjust_balance(plan.planner.means_account, plan.costs_p)
    adjust_balance(plan.planner.raw_material_account, plan.costs_r)
    adjust_balance(plan.planner.work_account, plan.costs_a)
    prd = plan.costs_p + plan.costs_r + plan.costs_a
    adjust_balance(plan.planner.product_account, -prd)

    # create Account for Social Accounting
    new_account = Account(
        id=10000,  # only a temporary workaround!
        account_owner=SocialAccounting(),
        account_type="accounting",
        balance=0,
        change_credit=lambda _: None,
    )

    AccountRepository().add(new_account)

    # register transactions
    transaction_1 = register_transaction(
        transaction_repository=TransactionRepository,
        account_from=new_account,
        account_to=plan.planner.means_account,
        amount=plan.costs_p,
        purpose=f"Plan-Id: {plan.id}",
    )

    transaction_2 = register_transaction(
        transaction_repository=TransactionRepository,
        account_from=new_account,
        account_to=plan.planner.raw_material_account,
        amount=plan.costs_r,
        purpose=f"Plan-Id: {plan.id}",
    )

    transaction_3 = register_transaction(
        transaction_repository=TransactionRepository,
        account_from=new_account,
        account_to=plan.planner.work_account,
        amount=plan.costs_a,
        purpose=f"Plan-Id: {plan.id}",
    )

    transaction_4 = register_transaction(
        transaction_repository=TransactionRepository,
        account_from=new_account,
        account_to=plan.planner.product_account,
        amount=-prd,
        purpose=f"Plan-Id: {plan.id}",
    )
