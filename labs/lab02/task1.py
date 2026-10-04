import hashlib
import hmac
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import ClassVar

PBKDF2_ITERATIONS = 600_000
SALT_SIZE = 16
SESSION_TIMEOUT_SEC = 900
EMAIL_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]{2,63}@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+")

LOGIN_SUCCESS = "login_success"
LOGIN_FAILURE = "login_failure"
LOGOUT = "logout"


class User:
    def __init__(self, username: str, email: str, role: str, active: bool):
        self.username = username
        self.email = email
        self.role = role
        self.active = active

        self.__password_hash = None
        self.__password_salt = None

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        if not isinstance(value, str) or not EMAIL_RE.fullmatch(value):
            raise ValueError(f"Invalid email: {value!r}")
        self._email = value

    def set_password(self, password: str):
        self.__password_salt = os.urandom(SALT_SIZE)
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), self.__password_salt, PBKDF2_ITERATIONS
        )
        self.__password_hash = digest

    def check_password(self, password: str) -> bool:
        if self.__password_hash is None or self.__password_salt is None:
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), self.__password_salt, PBKDF2_ITERATIONS
        )
        return hmac.compare_digest(digest, self.__password_hash)

    def deactivate(self):
        self.active = False

    def __str__(self):
        status = "active" if self.active else "inactive"
        return f"User(username={self.username}, email={self.email}, role={self.role}, {status})"


class Admin(User):
    def __init__(
        self, username: str, email: str, active: bool, permissions: set[str] | None
    ):
        super().__init__(username, email, "admin", active)
        self.permissions = set(permissions) if permissions else set()

    def grant_permission(self, permission: str):
        self.permissions.add(permission)

    def revoke_permission(self, permission: str):
        self.permissions.discard(permission)

    def has_peremission(self, permission: str) -> bool:
        return permission in self.permissions

    def __str__(self) -> str:
        return f"{super().__str__()} | permissions={sorted(self.permissions)}"


class Session:
    def __init__(self, ip: str, login_time: datetime, last_activity: datetime):
        self.ip = ip
        self.login_time = login_time
        self.last_activity = last_activity

    def touch(self):
        self.last_activity = datetime.now(timezone.utc)

    def is_active(self, timeout_sec: int) -> bool:
        if timeout_sec < 0:
            return False
        return (
            datetime.now(timezone.utc) - self.last_activity
        ).total_seconds() <= timeout_sec


@dataclass(frozen=True)
class AuditEntry:
    timestamp: datetime
    username: str
    action: str


class AuditLog:
    def __init__(self):
        self.entries = []

    def add_log(self, username: str, action: str):
        entry = AuditEntry(datetime.now(timezone.utc), username, action)
        self.entries.append(entry)

    def show_all(self):
        if len(self.entries) == 0:
            print("(no entries)")
            return
        for e in self.entries:
            print(f"{e.timestamp.isoformat()} | {e.username} | {e.action}")


class UserAccount:
    _KEY_TYPES: ClassVar[dict[str, type | tuple[type, ...]]] = {
        "user": User,
        "session": (Session, type(None)),
        "audit_log": AuditLog,
    }

    def __getitem__(self, key: str):
        if key not in self._KEY_TYPES:
            raise KeyError(key)
        return getattr(self, key)

    def __setitem__(self, key: str, value):
        if key not in self._KEY_TYPES:
            raise KeyError(key)
        if not isinstance(value, self._KEY_TYPES[key]):
            raise TypeError(
                f"{key!r} expects {self._KEY_TYPES[key]}, got {type(value).__name__}"
            )
        setattr(self, key, value)

    def __init__(self, username: str, email: str, role: str, active: bool):
        self.user = User(username, email, role, active)
        self.session = None
        self.auditlog = AuditLog()

    def login(self, username, password, ip):
        if (
            username != self.user.username
            or not self.user.active
            or not self.user.check_password(password)
        ):
            self.auditlog.add_log(username, LOGIN_FAILURE)
            return

        self.session = Session(
            ip, datetime.now(timezone.utc), datetime.now(timezone.utc)
        )
        self.session.touch()
        self.auditlog.add_log(username, LOGIN_SUCCESS)

    def is_authenticated(self) -> bool:
        return (
            self.session is not None
            and (
                datetime.now(timezone.utc) - self.session.last_activity
            ).total_seconds()
            <= SESSION_TIMEOUT_SEC
        )

    def logout(self):
        self.session = None
        self.auditlog.add_log(self.user.username, LOGOUT)
