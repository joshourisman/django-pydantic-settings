import urllib.parse
from inspect import getsourcefile
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Pattern, Sequence, Tuple, Union

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

import dj_database_url
from django.conf import global_settings, settings
from django.core.management.utils import get_random_secret_key
from pydantic import BaseSettings, DirectoryPath, Field, PyObject, validator
from pydantic.main import BaseModel
from pydantic.networks import EmailStr, IPvAnyAddress
from pydantic.types import FilePath

from .database import DatabaseDsn

DEFAULT_SETTINGS_MODULE_FIELD = Field(
    "pydantic_settings.settings.PydanticSettings", env="DJANGO_SETTINGS_MODULE"
)


class SetUp(BaseSettings):
    settings_module: PyObject = DEFAULT_SETTINGS_MODULE_FIELD
    settings_module_string: str = DEFAULT_SETTINGS_MODULE_FIELD

    def configure(self):
        if not settings.configured:
            settings_dict = {
                key: value
                for key, value in self.settings_module().dict().items()
                if hasattr(global_settings, key) is False
                or value != getattr(global_settings, key)
            }

            if settings_dict["BASE_DIR"] is None:
                base_dir = Path(
                    getsourcefile(SetUp().settings_module)
                    or "pydantic_settings.settings.PydanticSettings"
                ).parent.parent.parent
                settings_dict["BASE_DIR"] = base_dir
                base_module = self.settings_module_string.rsplit(".", 2)[0]
            else:
                base_module = f'{settings_dict["BASE_DIR"]}'

            if settings_dict["ROOT_URLCONF"] is None:
                settings_dict["ROOT_URLCONF"] = ".".join([base_module, "urls"])
            if settings_dict.get("WSGI_APPLICATION") is None:
                settings_dict["WSGI_APPLICATION"] = ".".join(
                    [base_module, "wsgi", "application"]
                )

            settings.configure(**settings_dict)


class DatabaseSettings(BaseSettings):
    default: Optional[DatabaseDsn] = Field(env="DATABASE_URL")

    @validator("*")
    def format_database_settings(cls, v):
        if v is None:
            return {}

        config = dj_database_url.parse(v)
        config["HOST"] = urllib.parse.unquote(config["HOST"])
        return config


class TemplateBackendModel(BaseModel):
    BACKEND: str
    NAME: Optional[str]
    DIRS: Optional[List[DirectoryPath]]
    APP_DIRS: Optional[bool]
    OPTIONS: Optional[dict]


class CacheBackendModel(BaseModel):
    default: Dict[Literal["BACKEND"], str]


def _get_default_setting(setting: str) -> Any:
    return getattr(global_settings, setting, None)


class PydanticSettings(BaseSettings):
    BASE_DIR: Optional[DirectoryPath]

    DEBUG: Optional[bool] = global_settings.DEBUG
    DEBUG_PROPAGATE_EXCEPTIONS: Optional[
        bool
    ] = global_settings.DEBUG_PROPAGATE_EXCEPTIONS
    ADMINS: Optional[List[Tuple[str, EmailStr]]] = _get_default_setting("ADMIN")
    INTERNAL_IPS: Optional[List[IPvAnyAddress]] = _get_default_setting("INTERNAL_IPS")

    # Would be nice to do something like Union[Literal["*"], IPvAnyAddress, AnyUrl], but there are a lot of different
    # options that need to be valid and don't necessarily fit those types.
    ALLOWED_HOSTS: Optional[List[str]] = global_settings.ALLOWED_HOSTS

    # Validate against actual list of valid TZs? https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List
    TIME_ZONE: Optional[str] = global_settings.TIME_ZONE
    USE_TZ: Optional[bool]

    # Validate LANGUAGE_CODE and LANGUAGES_BIDI against LANGUAGES.
    LANGUAGE_CODE: Optional[str] = global_settings.LANGUAGE_CODE
    LANGUAGES: Optional[List[Tuple[str, str]]] = global_settings.LANGUAGES
    LANGUAGES_BIDI: Optional[List[str]] = global_settings.LANGUAGES_BIDI

    USE_I18N: Optional[bool] = global_settings.USE_I18N
    LOCALE_PATHS: Optional[List[DirectoryPath]] = _get_default_setting("LOCALE_PATHS")
    LANGUAGE_COOKIE_NAME: Optional[str] = global_settings.LANGUAGE_COOKIE_NAME
    LANGUAGE_COOKIE_AGE: Optional[int] = global_settings.LANGUAGE_COOKIE_AGE
    LANGUAGE_COOKIE_DOMAIN: Optional[str] = global_settings.LANGUAGE_COOKIE_DOMAIN
    LANGUAGE_COOKIE_PATH: Optional[str] = global_settings.LANGUAGE_COOKIE_PATH
    LANGUAGE_COOKIE_SECURE: Optional[bool] = _get_default_setting(
        "LANGUAGE_COOKIE_SECURE"
    )
    LANGUAGE_COOKIE_HTTPONLY: Optional[bool] = _get_default_setting(
        "LANGUAGE_COOKIE_HTTPONLY"
    )
    LANGUAGE_COOKIE_SAMESITE: Optional[
        Literal["Lax", "Strict", "None"]
    ] = _get_default_setting("LANGUAGE_COOKIE_SAMESITE")
    USE_L10N: Optional[bool] = global_settings.USE_L10N
    MANAGERS: Optional[List[Tuple[str, EmailStr]]] = _get_default_setting("MANAGERS")
    DEFAULT_CHARSET: Optional[str] = global_settings.DEFAULT_CHARSET
    SERVER_EMAIL: Optional[
        Union[EmailStr, Literal["root@localhost"]]
    ] = global_settings.SERVER_EMAIL  # type: ignore

    DATABASES: Optional[DatabaseSettings] = Field({})
    DATABASE_ROUTERS: Optional[List[str]] = global_settings.DATABASE_ROUTERS  # type: ignore
    EMAIL_BACKEND: Optional[str] = global_settings.EMAIL_BACKEND
    EMAIL_HOST: Optional[str] = global_settings.EMAIL_HOST
    EMAIL_PORT: Optional[int] = global_settings.EMAIL_PORT
    EMAIL_USE_LOCALTIME: Optional[bool] = global_settings.EMAIL_USE_LOCALTIME
    EMAIL_HOST_USER: Optional[str] = global_settings.EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD: Optional[str] = global_settings.EMAIL_HOST_PASSWORD
    EMAIL_USE_TLS: Optional[bool] = global_settings.EMAIL_USE_TLS
    EMAIL_USE_SSL: Optional[bool] = global_settings.EMAIL_USE_SSL
    EMAIL_SSL_CERTFILE: Optional[FilePath] = global_settings.EMAIL_SSL_CERTFILE  # type: ignore
    EMAIL_SSL_KEYFILE: Optional[FilePath] = global_settings.EMAIL_SSL_KEYFILE  # type: ignore
    EMAIL_TIMEOUT: Optional[int] = global_settings.EMAIL_TIMEOUT
    INSTALLED_APPS: Optional[List[str]] = global_settings.INSTALLED_APPS
    TEMPLATES: Optional[List[TemplateBackendModel]] = global_settings.TEMPLATES  # type: ignore
    FORM_RENDERER: Optional[str] = global_settings.FORM_RENDERER
    DEFAULT_FROM_EMAIL: Optional[str] = global_settings.DEFAULT_FROM_EMAIL
    EMAIL_SUBJECT_PREFIX: Optional[str] = global_settings.EMAIL_SUBJECT_PREFIX
    APPEND_SLASH: Optional[bool] = global_settings.APPEND_SLASH
    PREPEND_WWW: Optional[bool] = global_settings.PREPEND_WWW
    FORCE_SCRIPT_NAME: Optional[str] = global_settings.FORCE_SCRIPT_NAME
    DISALLOWED_USER_AGENTS: Optional[
        List[Pattern]
    ] = global_settings.DISALLOWED_USER_AGENTS
    ABSOLUTE_URL_OVERRIDES: Optional[
        Dict[str, Callable]
    ] = global_settings.ABSOLUTE_URL_OVERRIDES
    IGNORABLE_404_URLS: Optional[List[Pattern]] = global_settings.IGNORABLE_404_URLS
    SECRET_KEY: str = Field(default_factory=get_random_secret_key)
    DEFAULT_FILE_STORAGE: Optional[str] = global_settings.DEFAULT_FILE_STORAGE
    MEDIA_ROOT: Optional[str] = global_settings.MEDIA_ROOT
    MEDIA_URL: Optional[str] = global_settings.MEDIA_URL
    STATIC_ROOT: Optional[DirectoryPath] = global_settings.STATIC_ROOT  # type: ignore
    STATIC_URL: Optional[str] = global_settings.STATIC_URL
    FILE_UPLOAD_HANDLERS: Optional[List[str]] = global_settings.FILE_UPLOAD_HANDLERS
    FILE_UPLOAD_MAX_MEMORY_SIZE: Optional[
        int
    ] = global_settings.FILE_UPLOAD_MAX_MEMORY_SIZE
    DATA_UPLOAD_MAX_MEMORY_SIZE: Optional[
        int
    ] = global_settings.DATA_UPLOAD_MAX_MEMORY_SIZE
    DATA_UPLOAD_MAX_NUMBER_FIELDS: Optional[
        int
    ] = global_settings.DATA_UPLOAD_MAX_NUMBER_FIELDS
    FILE_UPLOAD_TEMP_DIR: Optional[DirectoryPath] = global_settings.FILE_UPLOAD_TEMP_DIR  # type: ignore
    FILE_UPLOAD_PERMISSIONS: Optional[int] = global_settings.FILE_UPLOAD_PERMISSIONS
    FILE_UPLOAD_DIRECTORY_PERMISSIONS: Optional[
        int
    ] = global_settings.FILE_UPLOAD_DIRECTORY_PERMISSIONS
    FORMAT_MODULE_PATH: Optional[str] = global_settings.FORMAT_MODULE_PATH
    DATE_FORMAT: Optional[str] = global_settings.DATE_FORMAT
    DATETIME_FORMAT: Optional[str] = global_settings.DATETIME_FORMAT
    TIME_FORMAT: Optional[str] = global_settings.TIME_FORMAT
    YEAR_MONTH_FORMAT: Optional[str] = global_settings.YEAR_MONTH_FORMAT
    MONTH_DAY_FORMAT: Optional[str] = global_settings.MONTH_DAY_FORMAT
    SHORT_DATE_FORMAT: Optional[str] = global_settings.SHORT_DATE_FORMAT
    SHORT_DATETIME_FORMAT: Optional[str] = global_settings.SHORT_DATETIME_FORMAT
    DATE_INPUT_FORMATS: Optional[List[str]] = global_settings.DATE_INPUT_FORMATS
    TIME_INPUT_FORMATS: Optional[List[str]] = global_settings.TIME_INPUT_FORMATS
    DATETIME_INPUT_FORMATS: Optional[List[str]] = global_settings.DATETIME_INPUT_FORMATS
    FIRST_DAY_OF_WEEK: Optional[int] = global_settings.FIRST_DAY_OF_WEEK
    DECIMAL_SEPARATOR: Optional[str] = global_settings.DECIMAL_SEPARATOR
    USE_THOUSAND_SEPARATOR: Optional[bool] = global_settings.USE_THOUSAND_SEPARATOR
    THOUSAND_SEPARATOR: Optional[str] = global_settings.THOUSAND_SEPARATOR
    DEFAULT_TABLESPACE: Optional[str] = global_settings.DEFAULT_TABLESPACE
    DEFAULT_INDEX_TABLESPACE: Optional[str] = global_settings.DEFAULT_INDEX_TABLESPACE
    X_FRAME_OPTIONS: Optional[str] = global_settings.X_FRAME_OPTIONS
    USE_X_FORWARDED_HOST: Optional[bool] = global_settings.USE_X_FORWARDED_HOST
    USE_X_FORWARDED_PORT: Optional[bool] = global_settings.USE_X_FORWARDED_PORT
    WSGI_APPLICATION: Optional[str]
    SECURE_PROXY_SSL_HEADER: Optional[
        Tuple[str, str]
    ] = global_settings.SECURE_PROXY_SSL_HEADER
    DEFAULT_HASHING_ALGORITHM: Optional[
        Literal["sha1", "sha256"]
    ] = _get_default_setting("DEFAULT_HASHING_ALGORITHM")
    MIDDLEWARE: Optional[List[str]] = global_settings.MIDDLEWARE
    SESSION_CACHE_ALIAS: Optional[str] = global_settings.SESSION_CACHE_ALIAS
    SESSION_COOKIE_NAME: Optional[str] = global_settings.SESSION_COOKIE_NAME
    SESSION_COOKIE_AGE: Optional[int] = global_settings.SESSION_COOKIE_AGE
    SESSION_COOKIE_DOMAIN: Optional[str] = global_settings.SESSION_COOKIE_DOMAIN
    SESSION_COOKIE_SECURE: Optional[bool] = global_settings.SESSION_COOKIE_SECURE
    SESSION_COOKIE_PATH: Optional[str] = global_settings.SESSION_COOKIE_PATH
    SESSION_COOKIE_HTTPONLY: Optional[bool] = global_settings.SESSION_COOKIE_HTTPONLY
    SESSION_COOKIE_SAMESITE: Optional[
        Literal["Lax", "Strict", "None"]
    ] = _get_default_setting("SESSION_COOKIE_SAMESITE")  # type: ignore
    SESSION_SAVE_EVERY_REQUEST: Optional[
        bool
    ] = global_settings.SESSION_SAVE_EVERY_REQUEST
    SESSION_EXPIRE_AT_BROWSER_CLOSE: Optional[
        bool
    ] = global_settings.SESSION_EXPIRE_AT_BROWSER_CLOSE
    SESSION_ENGINE: Optional[str] = global_settings.SESSION_ENGINE
    SESSION_FILE_PATH: Optional[DirectoryPath] = global_settings.SESSION_FILE_PATH  # type: ignore
    SESSION_SERIALIZER: Optional[str] = global_settings.SESSION_SERIALIZER
    CACHES: Optional[CacheBackendModel] = global_settings.CACHES  # type: ignore
    CACHE_MIDDLEWARE_KEY_PREFIX: Optional[
        str
    ] = global_settings.CACHE_MIDDLEWARE_KEY_PREFIX
    CACHE_MIDDLEWARE_SECONDS: Optional[int] = global_settings.CACHE_MIDDLEWARE_SECONDS
    CACHE_MIDDLEWARE_ALIAS: Optional[str] = global_settings.CACHE_MIDDLEWARE_ALIAS
    AUTH_USER_MODEL: Optional[str] = global_settings.AUTH_USER_MODEL
    AUTHENTICATION_BACKENDS: Optional[
        Sequence[str]
    ] = global_settings.AUTHENTICATION_BACKENDS
    LOGIN_URL: Optional[str] = global_settings.LOGIN_URL
    LOGIN_REDIRECT_URL: Optional[str] = global_settings.LOGIN_REDIRECT_URL
    PASSWORD_RESET_TIMEOUT_DAYS: Optional[
        int
    ] = global_settings.PASSWORD_RESET_TIMEOUT_DAYS
    PASSWORD_RESET_TIMEOUT: Optional[int] = _get_default_setting(
        "PASSWORD_RESET_TIMEOUT"
    )
    PASSWORD_HASHERS: Optional[List[str]] = global_settings.PASSWORD_HASHERS
    AUTH_PASSWORD_VALIDATORS: Optional[
        List[dict]
    ] = global_settings.AUTH_PASSWORD_VALIDATORS
    SIGNING_BACKEND: Optional[str] = global_settings.SIGNING_BACKEND
    CSRF_FAILURE_VIEW: Optional[str] = global_settings.CSRF_FAILURE_VIEW
    CSRF_COOKIE_NAME: Optional[str] = global_settings.CSRF_COOKIE_NAME
    CSRF_COOKIE_AGE: Optional[int] = global_settings.CSRF_COOKIE_AGE
    CSRF_COOKIE_DOMAIN: Optional[str] = global_settings.CSRF_COOKIE_DOMAIN
    CSRF_COOKIE_PATH: Optional[str] = global_settings.CSRF_COOKIE_PATH
    CSRF_COOKIE_SECURE: Optional[bool] = global_settings.CSRF_COOKIE_SECURE
    CSRF_COOKIE_HTTPONLY: Optional[bool] = global_settings.CSRF_COOKIE_HTTPONLY
    CSRF_COOKIE_SAMESITE: Optional[
        Literal["Lax", "Strict", "None"]
    ] = _get_default_setting("CSRF_COOKIE_SAMESITE")  # type: ignore
    CSRF_HEADER_NAME: Optional[str] = global_settings.CSRF_HEADER_NAME
    CSRF_TRUSTED_ORIGINS: Optional[List[str]] = global_settings.CSRF_TRUSTED_ORIGINS
    CSRF_USE_SESSIONS: Optional[bool] = global_settings.CSRF_USE_SESSIONS
    MESSAGE_STORAGE: Optional[str] = global_settings.MESSAGE_STORAGE
    LOGGING_CONFIG: Optional[str] = global_settings.LOGGING_CONFIG
    LOGGING: Optional[dict] = global_settings.LOGGING
    DEFAULT_EXCEPTION_REPORTER: Optional[str] = _get_default_setting(
        "DEFAULT_EXCEPTION_REPORTER"
    )
    DEFAULT_EXCEPTION_REPORTER_FILTER: Optional[
        str
    ] = global_settings.DEFAULT_EXCEPTION_REPORTER_FILTER
    TEST_RUNNER: Optional[str] = global_settings.TEST_RUNNER
    TEST_NON_SERIALIZED_APPS: Optional[
        List[str]
    ] = global_settings.TEST_NON_SERIALIZED_APPS
    FIXTURE_DIRS: Optional[List[DirectoryPath]] = global_settings.FIXTURE_DIRS  # type: ignore
    STATICFILES_DIRS: Optional[List[DirectoryPath]] = global_settings.STATICFILES_DIRS  # type: ignore
    STATICFILES_STORAGE: Optional[str] = global_settings.STATICFILES_STORAGE
    STATICFILES_FINDERS: Optional[List[str]] = global_settings.STATICFILES_FINDERS
    MIGRATION_MODULES: Optional[Dict[str, str]] = global_settings.MIGRATION_MODULES
    SILENCED_SYSTEM_CHECKS: Optional[List[str]] = global_settings.SILENCED_SYSTEM_CHECKS
    SECURE_BROWSER_XSS_FILTER: Optional[
        bool
    ] = global_settings.SECURE_BROWSER_XSS_FILTER
    SECURE_CONTENT_TYPE_NOSNIFF: Optional[
        bool
    ] = global_settings.SECURE_CONTENT_TYPE_NOSNIFF
    SECURE_HSTS_INCLUDE_SUBDOMAINS: Optional[
        bool
    ] = global_settings.SECURE_HSTS_INCLUDE_SUBDOMAINS
    SECURE_HSTS_PRELOAD: Optional[bool] = global_settings.SECURE_HSTS_PRELOAD
    SECURE_HSTS_SECONDS: Optional[int] = global_settings.SECURE_HSTS_SECONDS
    SECURE_REDIRECT_EXEMPT: Optional[List[Pattern]] = global_settings.SECURE_REDIRECT_EXEMPT  # type: ignore
    SECURE_REFERRER_POLICY: Optional[
        Literal[
            "no-referrer",
            "no-referrer-when-downgrade",
            "origin",
            "origin-when-cross-origin",
            "same-origin",
            "strict-origin",
            "strict-origin-when-cross-origin",
            "unsafe-url",
        ]
    ] = _get_default_setting("SECURE_REFERRER_POLICY")
    SECURE_SSL_HOST: Optional[str] = global_settings.SECURE_SSL_HOST
    SECURE_SSL_REDIRECT: Optional[bool] = global_settings.SECURE_SSL_REDIRECT

    ROOT_URLCONF: Optional[str]
    STATIC_URL: Optional[str] = global_settings.STATIC_URL
    USE_I18N: Optional[bool] = global_settings.USE_I18N
    USE_L10N: Optional[bool] = global_settings.USE_L10N
    USE_TZ: Optional[bool] = global_settings.USE_TZ

    class Config:
        env_prefix = "DJANGO_"

    @validator("DATABASES")
    def remove_empty_database_dicts(cls, v):
        if v is None:
            return {}

        return {key: value for key, value in v.dict().items() if value != {}}
