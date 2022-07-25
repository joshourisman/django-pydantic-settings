import re
import urllib.parse
from typing import Dict, Optional, Pattern, Tuple, cast
from urllib.parse import quote_plus

from pydantic import AnyUrl, BaseSettings, Field, validator
from pydantic.validators import constr_length_validator, str_validator

_cloud_sql_regex_cache = None


def cloud_sql_regex() -> Pattern[str]:
    global _cloud_sql_regex_cache
    if _cloud_sql_regex_cache is None:
        _cloud_sql_regex_cache = re.compile(
            r"(?:(?P<scheme>[a-z][a-z0-9+\-.]+)://)?"  # scheme https://tools.ietf.org/html/rfc3986#appendix-A
            r"(?:(?P<user>[^\s:/]*)(?::(?P<password>[^\s/]*))?@)?"  # user info
            r"(?P<path>/[^\s?#]*)?",  # path
            re.IGNORECASE,
        )
    return _cloud_sql_regex_cache


class DatabaseDsn(AnyUrl):
    def __init__(
        self,
        url: str,
        *,
        scheme: str,
        user: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        tld: Optional[str] = None,
        host_type: str = "domain",
        port: Optional[str] = None,
        path: str = None,
        query: Optional[str] = None,
        fragment: Optional[str] = None,
    ) -> None:
        str.__init__(url)
        self.scheme = scheme
        self.user = user
        self.password = password
        self.host = host
        self.tld = tld
        self.host_type = host_type
        self.port = port
        self.path = path
        self.query = query
        self.fragment = fragment

    allowed_schemes = {
        "postgres",
        "postgresql",
        "postgis",
        "mssql",
        "mysql",
        "mysqlgis",
        "sqlite",
        "spatialite",
        "oracle",
        "oraclegis",
        "redshift",
    }

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
        cls, parts: Dict[str, str]
    ) -> Tuple[Optional[str], Optional[str], str, bool]:
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


class DatabaseSettings(BaseSettings):
    default: Optional[DatabaseDsn] = Field(env="DATABASE_URL")

    @validator("*")
    def format_database_settings(cls, v):
        if v is None:
            return {}

        engines = {
            "postgres": "django.db.backends.postgresql",
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

        return {
            "NAME": v.path[1:] if v.path.startswith("/") else v.path or "",
            "USER": v.user or "",
            "PASSWORD": v.password or "",
            "HOST": urllib.parse.unquote(v.host) if v.host else "",
            "PORT": v.port or "",
            "CONN_MAX_AGE": 0,
            "ENGINE": engines[v.scheme],
        }
