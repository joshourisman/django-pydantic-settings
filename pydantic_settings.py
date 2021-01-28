from django.conf import settings
import dj_database_url
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from pydantic import (
    AnyUrl,
    BaseSettings,
    DirectoryPath,
    Field,
    validator,
    PyObject,
)


class SetUp(BaseSettings):
    settings_module: PyObject = Field(
        "pydantic_settings.Settings", env="DJANGO_SETTINGS_MODULE"
    )

    def configure(self):
        settings.configure(**self.settings_module().dict())


class DjangoDsn(AnyUrl):
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

        return super().validate_host(cls, parts)  # type: ignore


class DatabaseSettings(BaseSettings):
    default: DjangoDsn = Field(env="DATABASE_URL")

    @validator("*")
    def format_database_settings(cls, v):
        return dj_database_url.parse(v)


class Settings(BaseSettings):
    BASE_DIR: DirectoryPath = Field(Path(__file__).resolve().parent.parent)
    SECRET_KEY: str = "$^ds)@-s8$d+59*3f=u7-h^@@x50hoa_!*w_!7yl-f-8pk5v+q"
    DEBUG: bool = True
    ALLOWED_HOSTS: List[str] = []
    INSTALLED_APPS: List[str] = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    ]
    MIDDLEWARE: List[str] = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]
    ROOT_URLCONF: str = "settings_test.urls"
    TEMPLATES: List[Dict] = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]
    WSGI_APPLICATION: str = "settings_test.wsgi.application"
    DATABASES: DatabaseSettings = Field({})
    AUTH_PASSWORD_VALIDATORS: List[Dict[str, str]] = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
        },
    ]
    LANGUAGE_CODE: str = "en-us"
    TIME_ZONE: str = "UTC"
    USE_I18N: bool = True
    USE_L10N: bool = True
    USE_TZ: bool = True
    STATIC_URL: str = "/static/"
