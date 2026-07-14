"""Cookie-based authentication."""

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

    data = json.loads(cookie_file.read_text(encoding="utf-8"))

    if isinstance(data, dict):
        cookies = {str(name): str(value) for name, value in data.items()}
    elif isinstance(data, list):
        cookies = {
            str(cookie["name"]): str(cookie["value"])
            for cookie in data
            if isinstance(cookie, dict) and "name" in cookie and "value" in cookie
        }
    else:
        raise ValueError("Invalid cookie file format")

    if "orm-jwt" not in cookies:
        raise ValueError("Missing orm-jwt cookie - are you logged into O'Reilly?")

    if not cookies["orm-jwt"]:
        raise ValueError("orm-jwt cookie is empty")

    return Session(cookies=cookies)
