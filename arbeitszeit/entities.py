from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Union
from uuid import UUID


@dataclass
class SocialAccounting:
    account: Account


@dataclass
class Member:
    id: UUID
    name: str
    email: str
    account: Account

    def accounts(self) -> List[Account]:
        return [self.account]


@dataclass
class Company:
    id: UUID
    email: str
    name: str
    means_account: Account
    raw_material_account: Account
    work_account: Account
    product_account: Account

    def accounts(self) -> List[Account]:
        return [
            self.means_account,
            self.raw_material_account,
            self.work_account,
            self.product_account,
        ]


class AccountTypes(Enum):
    p = "p"
    r = "r"
    a = "a"
    prd = "prd"
    member = "member"
    accounting = "accounting"


@dataclass
class Account:
    id: UUID
    account_type: AccountTypes


@dataclass
class ProductionCosts:
    labour_cost: Decimal
    resource_cost: Decimal
    means_cost: Decimal

    def total_cost(self) -> Decimal:
        return self.labour_cost + self.resource_cost + self.means_cost

    def __truediv__(self, other: Union[int, float]) -> ProductionCosts:
        denominator = Decimal(other)
        return ProductionCosts(
            labour_cost=self.labour_cost / denominator,
            resource_cost=self.resource_cost / denominator,
            means_cost=self.means_cost / denominator,
        )

    def __add__(self, other: ProductionCosts) -> ProductionCosts:
        return ProductionCosts(
            labour_cost=self.labour_cost + other.labour_cost,
            resource_cost=self.resource_cost + other.resource_cost,
            means_cost=self.means_cost + other.means_cost,
        )


@dataclass
class PlanDraft:
    id: UUID
    creation_date: datetime
    planner: Company
    production_costs: ProductionCosts
    product_name: str
    unit_of_distribution: str
    amount_produced: int
    description: str
    timeframe: int
    is_public_service: bool


@dataclass
class Plan:
    id: UUID
    plan_creation_date: datetime
    planner: Company
    production_costs: ProductionCosts
    prd_name: str
    prd_unit: str
    prd_amount: int
    description: str
    timeframe: int
    is_public_service: bool
    approved: bool
    approval_date: Optional[datetime]
    approval_reason: Optional[str]
    is_active: bool
    expired: bool
    renewed: bool
    activation_date: Optional[datetime]
    expiration_relative: Optional[int]
    expiration_date: Optional[datetime]
    last_certificate_payout: Optional[datetime]

    @property
    def price_per_unit(self) -> Decimal:
        cost_per_unit = self.production_costs.total_cost() / self.prd_amount
        return cost_per_unit if not self.is_public_service else Decimal(0)

    @property
    def expected_sales_value(self) -> Decimal:
        """
        For productive plans, sales value should equal total cost.
        Public services are not expected to sell,
        they give away their product for free.
        """
        return (
            self.production_costs.total_cost()
            if not self.is_public_service
            else Decimal(0)
        )


@dataclass
class ProductOffer:
    id: UUID
    name: str
    description: str
    plan: Plan


class PurposesOfPurchases(Enum):
    means_of_prod = "means_of_prod"
    raw_materials = "raw_materials"
    consumption = "consumption"


@dataclass
class Purchase:
    purchase_date: datetime
    plan: Plan
    buyer: Union[Member, Company]
    price_per_unit: Decimal
    amount: int
    purpose: PurposesOfPurchases


@dataclass
class Transaction:
    id: UUID
    date: datetime
    sending_account: Account
    receiving_account: Account
    amount: Decimal
    purpose: str

    def __hash__(self) -> int:
        return hash(self.id)
