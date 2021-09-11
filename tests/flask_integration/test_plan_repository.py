from datetime import datetime

from project.database.repositories import PlanRepository

from ..data_generators import PlanGenerator
from ..datetime_service import FakeDatetimeService
from .dependency_injection import injection_test


@injection_test
def test_get_approved_plans_created_before_returns_no_plans_by_default(
    repo: PlanRepository,
) -> None:
    plans = list(
        repo.get_approved_plans_created_before(
            datetime.min,
        )
    )
    assert not plans


@injection_test
def test_approved_plans_created_are_not_returned_when_querying_for_datetime_minimum(
    repo: PlanRepository, generator: PlanGenerator
) -> None:
    generator.create_plan(approved=True)
    plans = list(
        repo.get_approved_plans_created_before(
            datetime.min,
        )
    )
    assert not plans


@injection_test
def test_approved_plans_created_are_returned_when_querying_for_datetime_maximum(
    repo: PlanRepository, generator: PlanGenerator
) -> None:
    generator.create_plan(approved=True)
    plans = list(
        repo.get_approved_plans_created_before(
            datetime.max,
        )
    )
    assert len(plans) == 1


@injection_test
def test_when_querying_for_plans_created_before_date_then_plans_created_after_that_date_are_not_returned(
    repo: PlanRepository,
    generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
) -> None:
    datetime_service.freeze_time(datetime(year=2020, month=1, day=1))
    first_plan = generator.create_plan(approved=True)
    datetime_service.freeze_time(datetime(year=2021, month=1, day=1))
    plans = list(
        repo.get_approved_plans_created_before(
            datetime(year=2020, month=12, day=31),
        )
    )
    assert len(plans) == 1
    assert plans[0].id == first_plan.id
