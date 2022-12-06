from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any, Iterable, Sequence

from django.conf import global_settings, settings
from django.core.management.utils import get_random_secret_key
from pydantic import (
    BaseSettings,
    DirectoryPath,
    Field,
    PyObject,
    parse_obj_as,
    root_validator,
    validator,
)
from pydantic.fields import ModelField
from pydantic.types import FilePath

from pydantic_settings import types
from pydantic_settings.cache import CacheDsn
from pydantic_settings.database import DatabaseDsn

DEFAULT_SETTINGS_MODULE_FIELD = Field(
    "pydantic_settings.settings.PydanticSettings", env="DJANGO_SETTINGS_MODULE"
)


class SetUp(BaseSettings):
    DJANGO_SETTINGS_MODULE: PyObject = (
        "pydantic_settings.settings.PydanticSettings"  # type: ignore
    )

    def configure(self):
        if settings.configured:
            return False

        settings_obj: PydanticSettings
        # The settings module can either be a settings class, or an instance of a
        # settings class.
        if inspect.isclass(self.DJANGO_SETTINGS_MODULE):
            settings_obj = self.DJANGO_SETTINGS_MODULE()
        else:
            settings_obj = self.DJANGO_SETTINGS_MODULE  # type: ignore

        settings_dict = {
            key: value
            for key, value in settings_obj.dict().items()
            if key == key.upper()
            and (
                hasattr(global_settings, key) is False
                # Running the test suite can modify settings.DATABASES, so always
                # override the mutable global_settings.DATABASES.
                or key == "DATABASES"
                or value != getattr(global_settings, key)
            )
        }
        settings.configure(**settings_dict)
        return True


def _get_default_setting(setting: str) -> Any:
    return getattr(global_settings, setting, None)


class PydanticSettings(BaseSettings):
    BASE_DIR: types.BASE_DIR = None

    DEBUG: bool = global_settings.DEBUG
    DEBUG_PROPAGATE_EXCEPTIONS: bool = global_settings.DEBUG_PROPAGATE_EXCEPTIONS
    ADMINS: types.ADMINS = _get_default_setting("ADMIN")
    INTERNAL_IPS: types.INTERNAL_IPS = _get_default_setting("INTERNAL_IPS")

    # Would be nice to do something like Union[Literal["*"], IPvAnyAddress, AnyUrl], but
    # there are a lot of different options that need to be valid and don't necessarily
    # fit those types.
    ALLOWED_HOSTS: list[str] = global_settings.ALLOWED_HOSTS

    # Validate against actual list of valid TZs?
    # https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List
    TIME_ZONE: str = global_settings.TIME_ZONE
    USE_TZ: bool = global_settings.USE_TZ

    # Validate LANGUAGE_CODE and LANGUAGES_BIDI against LANGUAGES.
    LANGUAGE_CODE: str = global_settings.LANGUAGE_CODE
    LANGUAGES: types.LANGUAGES = global_settings.LANGUAGES
    LANGUAGES_BIDI: list[str] = global_settings.LANGUAGES_BIDI

    USE_I18N: bool = global_settings.USE_I18N
    LOCALE_PATHS: types.LOCALE_PATHS = _get_default_setting("LOCALE_PATHS")
    LANGUAGE_COOKIE_NAME: str = global_settings.LANGUAGE_COOKIE_NAME
    LANGUAGE_COOKIE_AGE: int | None = global_settings.LANGUAGE_COOKIE_AGE
    LANGUAGE_COOKIE_DOMAIN: str | None = global_settings.LANGUAGE_COOKIE_DOMAIN
    LANGUAGE_COOKIE_PATH: str = global_settings.LANGUAGE_COOKIE_PATH
    LANGUAGE_COOKIE_SECURE: bool | None = _get_default_setting("LANGUAGE_COOKIE_SECURE")
    LANGUAGE_COOKIE_HTTPONLY: bool | None = _get_default_setting(
        "LANGUAGE_COOKIE_HTTPONLY"
    )
    LANGUAGE_COOKIE_SAMESITE: types.LANGUAGE_COOKIE_SAMESITE = _get_default_setting(
        "LANGUAGE_COOKIE_SAMESITE"
    )
    USE_L10N: bool = global_settings.USE_L10N
    MANAGERS: types.MANAGERS = _get_default_setting("MANAGERS")
    DEFAULT_CHARSET: str = global_settings.DEFAULT_CHARSET
    SERVER_EMAIL: types.SERVER_EMAIL = (
        global_settings.SERVER_EMAIL  # type: ignore
    )

    DATABASES: types.DATABASES = global_settings.DATABASES  # type: ignore
    DATABASE_ROUTERS: list[str] = global_settings.DATABASE_ROUTERS  # type: ignore
    EMAIL_BACKEND: str = global_settings.EMAIL_BACKEND
    EMAIL_HOST: str = global_settings.EMAIL_HOST
    EMAIL_PORT: int = global_settings.EMAIL_PORT
    EMAIL_USE_LOCALTIME: bool = global_settings.EMAIL_USE_LOCALTIME
    EMAIL_HOST_USER: str = global_settings.EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD: str = global_settings.EMAIL_HOST_PASSWORD
    EMAIL_USE_TLS: bool = global_settings.EMAIL_USE_TLS
    EMAIL_USE_SSL: bool = global_settings.EMAIL_USE_SSL
    EMAIL_SSL_CERTFILE: FilePath | None = (
        global_settings.EMAIL_SSL_CERTFILE  # type: ignore
    )
    EMAIL_SSL_KEYFILE: FilePath | None = (
        global_settings.EMAIL_SSL_KEYFILE  # type: ignore
    )
    EMAIL_TIMEOUT: int | None = global_settings.EMAIL_TIMEOUT
    INSTALLED_APPS: list[str] = global_settings.INSTALLED_APPS
    TEMPLATES: types.TEMPLATES = global_settings.TEMPLATES  # type: ignore
    FORM_RENDERER: str = global_settings.FORM_RENDERER
    DEFAULT_FROM_EMAIL: str = global_settings.DEFAULT_FROM_EMAIL
    EMAIL_SUBJECT_PREFIX: str = global_settings.EMAIL_SUBJECT_PREFIX
    APPEND_SLASH: bool = global_settings.APPEND_SLASH
    PREPEND_WWW: bool = global_settings.PREPEND_WWW
    FORCE_SCRIPT_NAME: str | None = global_settings.FORCE_SCRIPT_NAME
    DISALLOWED_USER_AGENTS: types.DISALLOWED_USER_AGENTS = (
        global_settings.DISALLOWED_USER_AGENTS
    )
    ABSOLUTE_URL_OVERRIDES: types.ABSOLUTE_URL_OVERRIDES = (
        global_settings.ABSOLUTE_URL_OVERRIDES
    )
    IGNORABLE_404_URLS: types.IGNORABLE_404_URLS = global_settings.IGNORABLE_404_URLS
    SECRET_KEY: str = Field(default_factory=get_random_secret_key)
    DEFAULT_FILE_STORAGE: str = global_settings.DEFAULT_FILE_STORAGE
    MEDIA_ROOT: str = global_settings.MEDIA_ROOT
    MEDIA_URL: str = global_settings.MEDIA_URL
    STATIC_ROOT: DirectoryPath | None = global_settings.STATIC_ROOT  # type: ignore
    STATIC_URL: str | None = global_settings.STATIC_URL
    FILE_UPLOAD_HANDLERS: list[str] = global_settings.FILE_UPLOAD_HANDLERS
    FILE_UPLOAD_MAX_MEMORY_SIZE: int = global_settings.FILE_UPLOAD_MAX_MEMORY_SIZE
    DATA_UPLOAD_MAX_MEMORY_SIZE: int = global_settings.DATA_UPLOAD_MAX_MEMORY_SIZE
    DATA_UPLOAD_MAX_NUMBER_FIELDS: None | (
        int
    ) = global_settings.DATA_UPLOAD_MAX_NUMBER_FIELDS
    FILE_UPLOAD_TEMP_DIR: types.FILE_UPLOAD_TEMP_DIR = (
        global_settings.FILE_UPLOAD_TEMP_DIR  # type: ignore
    )
    FILE_UPLOAD_PERMISSIONS: int | None = global_settings.FILE_UPLOAD_PERMISSIONS
    FILE_UPLOAD_DIRECTORY_PERMISSIONS: None | (
        int
    ) = global_settings.FILE_UPLOAD_DIRECTORY_PERMISSIONS
    FORMAT_MODULE_PATH: str | None = global_settings.FORMAT_MODULE_PATH
    DATE_FORMAT: str = global_settings.DATE_FORMAT
    DATETIME_FORMAT: str = global_settings.DATETIME_FORMAT
    TIME_FORMAT: str = global_settings.TIME_FORMAT
    YEAR_MONTH_FORMAT: str = global_settings.YEAR_MONTH_FORMAT
    MONTH_DAY_FORMAT: str = global_settings.MONTH_DAY_FORMAT
    SHORT_DATE_FORMAT: str = global_settings.SHORT_DATE_FORMAT
    SHORT_DATETIME_FORMAT: str = global_settings.SHORT_DATETIME_FORMAT
    DATE_INPUT_FORMATS: list[str] = global_settings.DATE_INPUT_FORMATS
    TIME_INPUT_FORMATS: list[str] = global_settings.TIME_INPUT_FORMATS
    DATETIME_INPUT_FORMATS: list[str] = global_settings.DATETIME_INPUT_FORMATS
    FIRST_DAY_OF_WEEK: int = global_settings.FIRST_DAY_OF_WEEK
    DECIMAL_SEPARATOR: str = global_settings.DECIMAL_SEPARATOR
    USE_THOUSAND_SEPARATOR: bool = global_settings.USE_THOUSAND_SEPARATOR
    THOUSAND_SEPARATOR: str = global_settings.THOUSAND_SEPARATOR
    DEFAULT_TABLESPACE: str = global_settings.DEFAULT_TABLESPACE
    DEFAULT_INDEX_TABLESPACE: str = global_settings.DEFAULT_INDEX_TABLESPACE
    X_FRAME_OPTIONS: str = global_settings.X_FRAME_OPTIONS
    USE_X_FORWARDED_HOST: bool = global_settings.USE_X_FORWARDED_HOST
    USE_X_FORWARDED_PORT: bool = global_settings.USE_X_FORWARDED_PORT
    WSGI_APPLICATION: str | None = None
    SECURE_PROXY_SSL_HEADER: types.SECURE_PROXY_SSL_HEADER = (
        global_settings.SECURE_PROXY_SSL_HEADER
    )
    DEFAULT_HASHING_ALGORITHM: types.DEFAULT_HASHING_ALGORITHM = _get_default_setting(
        "DEFAULT_HASHING_ALGORITHM"
    )
    MIDDLEWARE: list[str] = global_settings.MIDDLEWARE
    SESSION_CACHE_ALIAS: str = global_settings.SESSION_CACHE_ALIAS
    SESSION_COOKIE_NAME: str = global_settings.SESSION_COOKIE_NAME
    SESSION_COOKIE_AGE: int | None = global_settings.SESSION_COOKIE_AGE
    SESSION_COOKIE_DOMAIN: str | None = global_settings.SESSION_COOKIE_DOMAIN
    SESSION_COOKIE_SECURE: bool = global_settings.SESSION_COOKIE_SECURE
    SESSION_COOKIE_PATH: str = global_settings.SESSION_COOKIE_PATH
    SESSION_COOKIE_HTTPONLY: bool = global_settings.SESSION_COOKIE_HTTPONLY
    SESSION_COOKIE_SAMESITE: types.SESSION_COOKIE_SAMESITE = _get_default_setting(
        "SESSION_COOKIE_SAMESITE"
    )
    SESSION_SAVE_EVERY_REQUEST: bool = global_settings.SESSION_SAVE_EVERY_REQUEST
    SESSION_EXPIRE_AT_BROWSER_CLOSE: bool = (
        global_settings.SESSION_EXPIRE_AT_BROWSER_CLOSE
    )
    SESSION_ENGINE: str = global_settings.SESSION_ENGINE
    SESSION_FILE_PATH: types.SESSION_FILE_PATH = (
        global_settings.SESSION_FILE_PATH  # type: ignore
    )
    SESSION_SERIALIZER: str = global_settings.SESSION_SERIALIZER
    CACHES: types.CACHES = global_settings.CACHES  # type: ignore
    CACHE_MIDDLEWARE_KEY_PREFIX: str = global_settings.CACHE_MIDDLEWARE_KEY_PREFIX
    CACHE_MIDDLEWARE_SECONDS: int | None = global_settings.CACHE_MIDDLEWARE_SECONDS
    CACHE_MIDDLEWARE_ALIAS: str = global_settings.CACHE_MIDDLEWARE_ALIAS
    AUTH_USER_MODEL: str = global_settings.AUTH_USER_MODEL
    AUTHENTICATION_BACKENDS: Sequence[str] = global_settings.AUTHENTICATION_BACKENDS
    LOGIN_URL: str = global_settings.LOGIN_URL
    LOGIN_REDIRECT_URL: str = global_settings.LOGIN_REDIRECT_URL
    PASSWORD_RESET_TIMEOUT_DAYS: int | None = _get_default_setting(
        "PASSWORD_RESET_TIMEOUT_DAYS"
    )
    PASSWORD_RESET_TIMEOUT: int | None = _get_default_setting("PASSWORD_RESET_TIMEOUT")
    PASSWORD_HASHERS: list[str] = global_settings.PASSWORD_HASHERS
    AUTH_PASSWORD_VALIDATORS: list[dict] = global_settings.AUTH_PASSWORD_VALIDATORS
    SIGNING_BACKEND: str = global_settings.SIGNING_BACKEND
    CSRF_FAILURE_VIEW: str = global_settings.CSRF_FAILURE_VIEW
    CSRF_COOKIE_NAME: str = global_settings.CSRF_COOKIE_NAME
    CSRF_COOKIE_AGE: int | None = global_settings.CSRF_COOKIE_AGE
    CSRF_COOKIE_DOMAIN: str | None = global_settings.CSRF_COOKIE_DOMAIN
    CSRF_COOKIE_PATH: str = global_settings.CSRF_COOKIE_PATH
    CSRF_COOKIE_SECURE: bool = global_settings.CSRF_COOKIE_SECURE
    CSRF_COOKIE_HTTPONLY: bool = global_settings.CSRF_COOKIE_HTTPONLY
    CSRF_COOKIE_SAMESITE: types.CSRF_COOKIE_SAMESITE = _get_default_setting(
        "CSRF_COOKIE_SAMESITE"
    )
    CSRF_HEADER_NAME: str = global_settings.CSRF_HEADER_NAME
    CSRF_TRUSTED_ORIGINS: list[str] = global_settings.CSRF_TRUSTED_ORIGINS
    CSRF_USE_SESSIONS: bool = global_settings.CSRF_USE_SESSIONS
    MESSAGE_STORAGE: str = global_settings.MESSAGE_STORAGE
    LOGGING_CONFIG: str = global_settings.LOGGING_CONFIG
    LOGGING: dict = global_settings.LOGGING
    DEFAULT_EXCEPTION_REPORTER: str | None = _get_default_setting(
        "DEFAULT_EXCEPTION_REPORTER"
    )
    DEFAULT_EXCEPTION_REPORTER_FILTER: str = (
        global_settings.DEFAULT_EXCEPTION_REPORTER_FILTER
    )
    TEST_RUNNER: str = global_settings.TEST_RUNNER
    TEST_NON_SERIALIZED_APPS: list[str] = global_settings.TEST_NON_SERIALIZED_APPS
    FIXTURE_DIRS: types.FIXTURE_DIRS = global_settings.FIXTURE_DIRS  # type: ignore
    STATICFILES_DIRS: types.STATICFILES_DIRS = (
        global_settings.STATICFILES_DIRS  # type: ignore
    )
    STATICFILES_STORAGE: str = global_settings.STATICFILES_STORAGE
    STATICFILES_FINDERS: list[str] = global_settings.STATICFILES_FINDERS
    MIGRATION_MODULES: dict[str, str] = global_settings.MIGRATION_MODULES
    SILENCED_SYSTEM_CHECKS: list[str] = global_settings.SILENCED_SYSTEM_CHECKS
    SECURE_BROWSER_XSS_FILTER: bool | None = _get_default_setting(
        "SECURE_BROWSER_XSS_FILTER"
    )
    SECURE_CONTENT_TYPE_NOSNIFF: bool = global_settings.SECURE_CONTENT_TYPE_NOSNIFF
    SECURE_HSTS_INCLUDE_SUBDOMAINS: bool = (
        global_settings.SECURE_HSTS_INCLUDE_SUBDOMAINS
    )
    SECURE_HSTS_PRELOAD: bool = global_settings.SECURE_HSTS_PRELOAD
    SECURE_HSTS_SECONDS: int | None = global_settings.SECURE_HSTS_SECONDS
    SECURE_REDIRECT_EXEMPT: types.SECURE_REDIRECT_EXEMPT = (
        global_settings.SECURE_REDIRECT_EXEMPT
    )
    SECURE_REFERRER_POLICY: types.SECURE_REFERRER_POLICY = _get_default_setting(
        "SECURE_REFERRER_POLICY"
    )
    SECURE_SSL_HOST: str | None = global_settings.SECURE_SSL_HOST
    SECURE_SSL_REDIRECT: bool = global_settings.SECURE_SSL_REDIRECT

    ROOT_URLCONF: str | None = None

    default_database_dsn: DatabaseDsn | None = Field(
        env="DATABASE_URL", configure_database="default"
    )
    default_cache_dsn: CacheDsn | None = Field(
        env="CACHE_URL", configure_cache="default"
    )

    class Config:
        env_prefix = "DJANGO_"

    @validator("DATABASES", pre=True)
    def parse_databases(cls, databases: dict) -> dict:
        """
        Parse any databases specified as DSNs into DatabaseModel objects.
        """
        parsed_databases = {}
        for key, value in databases.items():
            if value and isinstance(value, str) and not isinstance(value, DatabaseDsn):
                value = parse_obj_as(DatabaseDsn, value)
            if isinstance(value, DatabaseDsn):
                value = value.to_settings_model()
            if value:
                parsed_databases[key] = value
        return parsed_databases

    @root_validator
    def set_default_database(cls, values: dict) -> dict:
        """
        Set the default database if it is not already set and is provided by
        default_database_dsn field.
        """
        DATABASES = values["DATABASES"]
        for db_key, attr in cls._get_dsn_fields(field_extra="configure_database"):
            if not DATABASES.get(db_key):
                database_dsn: DatabaseDsn | None = values[attr]
                if database_dsn:
                    DATABASES[db_key] = database_dsn.to_settings_model()
            del values[attr]
        return values

    @root_validator
    def set_default_cache(cls, values: dict) -> dict:
        """
        Set the default cache if it is not already set and is provided by
        default_cache_dsn field.
        """
        CACHES = values.get("CACHES") or {}
        for cache_key, attr in cls._get_dsn_fields(field_extra="configure_cache"):
            cache_dsn: CacheDsn | None = values[attr]
            if cache_dsn:
                CACHES = values.setdefault("CACHES", {})
                CACHES[cache_key] = cache_dsn.to_settings_model()
            del values[attr]
        return values

    @classmethod
    def _get_dsn_fields(cls, field_extra: str) -> Iterable[tuple[str, str]]:
        field: ModelField
        for field in cls.__fields__.values():
            db_key = field.field_info.extra.get(field_extra)
            if db_key:
                yield db_key, field.name

    @root_validator
    def get_dynamic_defaults(cls, values):
        """
        Get dynamic defaults for BASE_DIR, ROOT_URLCONF and WSGI_APPLICATION.

        If any of these settings are not explicitly set, and a custom `PydanticSettings`
        class is being used then ROOT_URLCONF and WSGI_APPLICATION will be prepended
        with the settings root module and BASE_DIR will be set to the parent directory
        containing the root module package.
        """
        module = inspect.getmodule(cls)
        if not module or module.__name__.startswith("pydantic_settings."):
            return values

        project_module_name = module.__name__.split(".", 1)[0]
        if project_module_name:
            if not values["WSGI_APPLICATION"]:
                values["WSGI_APPLICATION"] = f"{project_module_name}.wsgi.application"
            if not values["ROOT_URLCONF"]:
                values["ROOT_URLCONF"] = f"{project_module_name}.urls"

        base_dir: Path | None = values["BASE_DIR"]
        if not base_dir:
            ancestor = module.__name__.count(".")
            path = Path(inspect.getfile(module)).resolve()
            if path.stem == "__init__":
                ancestor += 1
            values["BASE_DIR"] = path.parents[ancestor]

        return values
