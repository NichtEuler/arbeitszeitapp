from functools import wraps
from typing import Any, Callable
from uuid import UUID

from flask import Blueprint, redirect, session, url_for
from flask_login import current_user, login_required

from arbeitszeit_flask import types
from arbeitszeit_flask.database.repositories import MemberRepository
from arbeitszeit_flask.dependency_injection import MemberModule, with_injection

main_member = Blueprint(
    "main_member", __name__, template_folder="templates", static_folder="static"
)


class MemberRoute:
    def __init__(self, route_string: str, methods=None):
        self.route_string = route_string
        if methods is None:
            self.methods = ["GET"]
        else:
            self.methods = methods

    def __call__(self, view_function: Callable[..., types.Response]):
        @wraps(view_function)
        def _wrapper(*args: Any, **kwargs: Any) -> types.Response:
            if not user_is_member():
                return redirect(url_for("auth.zurueck"))
            return view_function(*args, **kwargs)

        return self._apply_decorators(_wrapper)

    def _apply_decorators(self, function):
        injection = with_injection([MemberModule()])
        return main_member.route(self.route_string, methods=self.methods)(
            injection(login_required(injection(check_confirmed)(function)))
        )


def user_is_member():
    return session.get("user_type") == "member"


def check_confirmed(func, member_repository: MemberRepository):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not member_repository.is_member_confirmed(UUID(current_user.id)):
            return redirect(url_for("auth.unconfirmed_member"))
        return func(*args, **kwargs)

    return decorated_function
