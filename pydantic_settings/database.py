from __future__ import annotations

import re
import urllib.parse
from typing import Pattern, cast
from urllib.parse import quote_plus

from pydantic import AnyUrl
from pydantic.validators import constr_length_validator, str_validator

from pydantic_settings.models import DatabaseModel

_cloud_sql_regex_cache = None


DB_ENGINES = {
    "postgres": "django.db.backends.postgresql",
    "postgresql": "django.db.backends.postgresql",
    "postgis": "django.contrib.gis.db.backends.postgis",
    "mssql": "sql_server.pyodbc",
    "mysql": "django.db.backends.mysql",
    "mysqlgis": "django.contrib.gis.db.backends.mysql",
    "sqlite": "django.db.backends.sqlite3",
    "spatialite": "django.contrib.gis.db.backends.spatialite",
    "oracle": "django.db.backends.oracle",
    "oraclegis": "django.contrib.gis.db.backends.oracle",
    "redshift": "django_redshift_backend",
}


def cloud_sql_regex() -> Pattern[str]:
    global _cloud_sql_regex_cache
    if _cloud_sql_regex_cache is None:
        _cloud_sql_regex_cache = re.compile(
            # scheme https://tools.ietf.org/html/rfc3986#appendix-A
            r"(?:(?P<scheme>[a-z][a-z0-9+\-.]+)://)?"
            r"(?:(?P<user>[^\s:/]*)(?::(?P<password>[^\s/]*))?@)?"  # user info
            r"(?P<path>/[^\s?#]*)?",  # path
            re.IGNORECASE,
        )
    return _cloud_sql_regex_cache


class DatabaseDsn(AnyUrl):
    allowed_schemes = set(DB_ENGINES)

    @classmethod
    def validate(cls, value, field, config):
        if value.__class__ == cls:
            return value

        value = str_validator(value)
        if cls.strip_whitespace:
            value = value.strip()

        url: str = cast(str, constr_length_validator(value, field, config))

        if "/cloudsql/" in url:
            m = cloud_sql_regex().match(url)
            if m:
                parts = m.groupdict()
                socket, path = parts["path"].rsplit("/", 1)
                escaped_socket = quote_plus(socket)
                escaped_dsn = value.replace(socket, escaped_socket)
                return super().validate(escaped_dsn, field, config)

        return super().validate(value, field, config)

    @classmethod
    def validate_host(
        cls, parts: dict[str, str]
    ) -> tuple[str | None, str | None, str, bool]:
        host = None
        for f in ("domain", "ipv4", "ipv6"):
            host = parts[f]
            if host:
                break

        if host is None:
            return None, None, "file", False

        if host.startswith("%2F"):
            return host, None, "socket", False

        return super().validate_host(parts)

    def to_settings_model(self) -> DatabaseModel:
        name = self.path
        if name and name.startswith("/"):
            name = name[1:]
        return DatabaseModel(
            NAME=name or "",
            USER=self.user or "",
            PASSWORD=self.password or "",
            HOST=urllib.parse.unquote(self.host) if self.host else "",
            PORT=self.port or "",
            ENGINE=DB_ENGINES[self.scheme],
        )
