from typing import Optional

from flask import current_app
from injector import singleton
from itsdangerous import URLSafeTimedSerializer


@singleton
class FlaskTokenService:
    def __init__(self) -> None:
        self.serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

    def generate_token(self, input: str) -> str:
        token = self.serializer.dumps(
            input, salt=current_app.config["SECURITY_PASSWORD_SALT"]
        )
        assert isinstance(token, str)
        return token

    def confirm_token(self, token: str, max_age_in_sec: int = 3600) -> Optional[str]:
        return self._load_token(token, max_age_in_seconds=max_age_in_sec)

    def unwrap_invitation_token(self, token: str) -> Optional[str]:
        return self._load_token(token=token, max_age_in_seconds=7 * 24 * 3600)  # 1 week

    def _load_token(
        self, token: str, max_age_in_seconds: Optional[int] = None
    ) -> Optional[str]:
        return self.serializer.loads(
            token,
            salt=current_app.config["SECURITY_PASSWORD_SALT"],
            max_age=max_age_in_seconds,
        )
