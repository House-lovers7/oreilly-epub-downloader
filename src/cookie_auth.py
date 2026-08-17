"""Cookie-based authentication."""

import base64
import datetime as dt
import json
import os
import stat
from dataclasses import dataclass
from pathlib import Path

import httpx


DEFAULT_COOKIE_DOMAIN = "learning.oreilly.com"


@dataclass
class Session:
    """Authenticated session."""

    cookies: dict[str, str]

    def get_cookie_header(self) -> str:
        """Format cookies for HTTP header."""
        return "; ".join(f"{k}={v}" for k, v in self.cookies.items())

    def to_cookie_jar(self, domain: str = DEFAULT_COOKIE_DOMAIN) -> httpx.Cookies:
        """Create a host-scoped cookie jar.

        A manually configured global ``Cookie`` header is sent to every host the
        client contacts.  A cookie jar preserves browser-like domain scoping and
        therefore keeps subscription credentials off third-party asset origins.
        """
        jar = httpx.Cookies()
        for name, value in self.cookies.items():
            jar.set(name, value, domain=domain, path="/")
        return jar


def _cookie_map(data: object) -> dict[str, str]:
    """Normalise the supported cookie file shapes into a flat mapping.

    Besides the object and array exports, a string is unwrapped once: the
    DevTools console renders a ``JSON.stringify`` result as a quoted literal,
    so copying what the console shows saves the export with one extra layer of
    encoding.  Anything that does not unwrap into an object or array keeps the
    original rejection.
    """
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except ValueError:
            pass
    if isinstance(data, dict):
        return {str(name): str(value) for name, value in data.items()}
    if isinstance(data, list):
        return {
            str(cookie["name"]): str(cookie["value"])
            for cookie in data
            if isinstance(cookie, dict) and "name" in cookie and "value" in cookie
        }
    raise ValueError("Invalid cookie file format")


def decode_jwt_expiry(token: str) -> dt.datetime | None:
    """Read the ``exp`` claim of a JWT, or None when the token is opaque.

    A session value is not required to be a JWT, so anything undecodable is
    reported as unknown expiry rather than treated as invalid.
    """
    parts = token.split(".")
    if len(parts) != 3:
        return None

    payload = parts[1] + "=" * (-len(parts[1]) % 4)
    try:
        expiry = json.loads(base64.urlsafe_b64decode(payload))["exp"]
    except (ValueError, KeyError, TypeError):
        return None

    if isinstance(expiry, bool) or not isinstance(expiry, int | float):
        return None
    try:
        return dt.datetime.fromtimestamp(expiry, dt.UTC)
    except (OSError, OverflowError, ValueError):
        return None


def peek_jwt_expiry(cookie_file: Path) -> dt.datetime | None:
    """Probe token expiry for offline planning without ever raising.

    Planning stays informational: a cookie file that execution would reject
    must still produce a plan, so every read problem maps to unknown expiry.
    """
    try:
        cookies = _cookie_map(json.loads(cookie_file.read_text(encoding="utf-8")))
    except (OSError, ValueError):
        return None

    token = cookies.get("orm-jwt")
    return decode_jwt_expiry(token) if token else None


def load_cookies(cookie_file: Path) -> Session:
    """Load session from a JSON cookie file."""
    if not cookie_file.is_file():
        raise ValueError(f"Cookie path is not a regular file: {cookie_file}")

    if os.name == "posix":
        mode = stat.S_IMODE(cookie_file.stat().st_mode)
        if mode & 0o077:
            raise PermissionError(
                f"Cookie file permissions are too broad ({mode:04o}); "
                f"run: chmod 600 {cookie_file}"
            )

    cookies = _cookie_map(json.loads(cookie_file.read_text(encoding="utf-8")))

    if "orm-jwt" not in cookies:
        raise ValueError("Missing orm-jwt cookie - are you logged into O'Reilly?")

    if not cookies["orm-jwt"]:
        raise ValueError("orm-jwt cookie is empty")

    expiry = decode_jwt_expiry(cookies["orm-jwt"])
    if expiry is not None and expiry <= dt.datetime.now(dt.UTC):
        raise PermissionError(
            f"orm-jwt expired at {expiry.isoformat()}; re-export {cookie_file} "
            "from the browser and rerun immediately - the token is short-lived"
        )

    return Session(cookies=cookies)
