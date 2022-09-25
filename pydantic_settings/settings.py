from inspect import getsourcefile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

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
    settings_module: PyObject = DEFAULT_SETTINGS_MODULE_FIELD
    settings_module_string: str = DEFAULT_SETTINGS_MODULE_FIELD

    def configure(self):
        if not settings.configured:
            settings_dict = {
                key: value
                for key, value in self.settings_module().dict().items()
                if (
                    hasattr(global_settings, key) is False
                    # Running the test suite can modify settings.DATABASES, so always
                    # override the mutable global_settings.DATABASES.
                    or key == "DATABASES"
                    or value != getattr(global_settings, key)
                )
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
    ALLOWED_HOSTS: List[str] = global_settings.ALLOWED_HOSTS

    # Validate against actual list of valid TZs?
    # https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List
    TIME_ZONE: str = global_settings.TIME_ZONE
    USE_TZ: bool = global_settings.USE_TZ

    # Validate LANGUAGE_CODE and LANGUAGES_BIDI against LANGUAGES.
    LANGUAGE_CODE: str = global_settings.LANGUAGE_CODE
    LANGUAGES: types.LANGUAGES = global_settings.LANGUAGES
    LANGUAGES_BIDI: List[str] = global_settings.LANGUAGES_BIDI

    USE_I18N: bool = global_settings.USE_I18N
    LOCALE_PATHS: types.LOCALE_PATHS = _get_default_setting("LOCALE_PATHS")
    LANGUAGE_COOKIE_NAME: str = global_settings.LANGUAGE_COOKIE_NAME
    LANGUAGE_COOKIE_AGE: Optional[int] = global_settings.LANGUAGE_COOKIE_AGE
    LANGUAGE_COOKIE_DOMAIN: Optional[str] = global_settings.LANGUAGE_COOKIE_DOMAIN
    LANGUAGE_COOKIE_PATH: str = global_settings.LANGUAGE_COOKIE_PATH
    LANGUAGE_COOKIE_SECURE: Optional[bool] = _get_default_setting(
        "LANGUAGE_COOKIE_SECURE"
    )
    LANGUAGE_COOKIE_HTTPONLY: Optional[bool] = _get_default_setting(
        "LANGUAGE_COOKIE_HTTPONLY"
    )
    LANGUAGE_COOKIE_SAMESITE: types.LANGUAGE_COOKIE_SAMESITE = _get_default_setting(
        "LANGUAGE_COOKIE_SAMESITE"
    )
    USE_L10N: bool = global_settings.USE_L10N
    MANAGERS: types.MANAGERS = _get_default_setting("MANAGERS")
    DEFAULT_CHARSET: str = global_settings.DEFAULT_CHARSET
    SERVER_EMAIL: types.SERVER_EMAIL = global_settings.SERVER_EMAIL

    DATABASES: types.DATABASES = global_settings.DATABASES  # type: ignore
    DATABASE_ROUTERS: List[str] = global_settings.DATABASE_ROUTERS
    EMAIL_BACKEND: str = global_settings.EMAIL_BACKEND
    EMAIL_HOST: str = global_settings.EMAIL_HOST
    EMAIL_PORT: int = global_settings.EMAIL_PORT
    EMAIL_USE_LOCALTIME: bool = global_settings.EMAIL_USE_LOCALTIME
    EMAIL_HOST_USER: str = global_settings.EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD: str = global_settings.EMAIL_HOST_PASSWORD
    EMAIL_USE_TLS: bool = global_settings.EMAIL_USE_TLS
    EMAIL_USE_SSL: bool = global_settings.EMAIL_USE_SSL
    EMAIL_SSL_CERTFILE: Optional[FilePath] = global_settings.EMAIL_SSL_CERTFILE
    EMAIL_SSL_KEYFILE: Optional[FilePath] = global_settings.EMAIL_SSL_KEYFILE
    EMAIL_TIMEOUT: Optional[int] = global_settings.EMAIL_TIMEOUT
    INSTALLED_APPS: List[str] = global_settings.INSTALLED_APPS
    TEMPLATES: types.TEMPLATES = global_settings.TEMPLATES
    FORM_RENDERER: str = global_settings.FORM_RENDERER
    DEFAULT_FROM_EMAIL: str = global_settings.DEFAULT_FROM_EMAIL
    EMAIL_SUBJECT_PREFIX: str = global_settings.EMAIL_SUBJECT_PREFIX
    APPEND_SLASH: bool = global_settings.APPEND_SLASH
    PREPEND_WWW: bool = global_settings.PREPEND_WWW
    FORCE_SCRIPT_NAME: Optional[str] = global_settings.FORCE_SCRIPT_NAME
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
    STATIC_ROOT: Optional[DirectoryPath] = global_settings.STATIC_ROOT
    STATIC_URL: Optional[str] = global_settings.STATIC_URL
    FILE_UPLOAD_HANDLERS: List[str] = global_settings.FILE_UPLOAD_HANDLERS
    FILE_UPLOAD_MAX_MEMORY_SIZE: int = global_settings.FILE_UPLOAD_MAX_MEMORY_SIZE
    DATA_UPLOAD_MAX_MEMORY_SIZE: int = global_settings.DATA_UPLOAD_MAX_MEMORY_SIZE
    DATA_UPLOAD_MAX_NUMBER_FIELDS: Optional[
        int
    ] = global_settings.DATA_UPLOAD_MAX_NUMBER_FIELDS
    FILE_UPLOAD_TEMP_DIR: types.FILE_UPLOAD_TEMP_DIR = (
        global_settings.FILE_UPLOAD_TEMP_DIR
    )
    FILE_UPLOAD_PERMISSIONS: Optional[int] = global_settings.FILE_UPLOAD_PERMISSIONS
    FILE_UPLOAD_DIRECTORY_PERMISSIONS: Optional[
        int
    ] = global_settings.FILE_UPLOAD_DIRECTORY_PERMISSIONS
    FORMAT_MODULE_PATH: Optional[str] = global_settings.FORMAT_MODULE_PATH
    DATE_FORMAT: str = global_settings.DATE_FORMAT
    DATETIME_FORMAT: str = global_settings.DATETIME_FORMAT
    TIME_FORMAT: str = global_settings.TIME_FORMAT
    YEAR_MONTH_FORMAT: str = global_settings.YEAR_MONTH_FORMAT
    MONTH_DAY_FORMAT: str = global_settings.MONTH_DAY_FORMAT
    SHORT_DATE_FORMAT: str = global_settings.SHORT_DATE_FORMAT
    SHORT_DATETIME_FORMAT: str = global_settings.SHORT_DATETIME_FORMAT
    DATE_INPUT_FORMATS: List[str] = global_settings.DATE_INPUT_FORMATS
    TIME_INPUT_FORMATS: List[str] = global_settings.TIME_INPUT_FORMATS
    DATETIME_INPUT_FORMATS: List[str] = global_settings.DATETIME_INPUT_FORMATS
    FIRST_DAY_OF_WEEK: int = global_settings.FIRST_DAY_OF_WEEK
    DECIMAL_SEPARATOR: str = global_settings.DECIMAL_SEPARATOR
    USE_THOUSAND_SEPARATOR: bool = global_settings.USE_THOUSAND_SEPARATOR
    THOUSAND_SEPARATOR: str = global_settings.THOUSAND_SEPARATOR
    DEFAULT_TABLESPACE: str = global_settings.DEFAULT_TABLESPACE
    DEFAULT_INDEX_TABLESPACE: str = global_settings.DEFAULT_INDEX_TABLESPACE
    X_FRAME_OPTIONS: str = global_settings.X_FRAME_OPTIONS
    USE_X_FORWARDED_HOST: bool = global_settings.USE_X_FORWARDED_HOST
    USE_X_FORWARDED_PORT: bool = global_settings.USE_X_FORWARDED_PORT
    WSGI_APPLICATION: Optional[str] = None
    SECURE_PROXY_SSL_HEADER: types.SECURE_PROXY_SSL_HEADER = (
        global_settings.SECURE_PROXY_SSL_HEADER
    )
    DEFAULT_HASHING_ALGORITHM: types.DEFAULT_HASHING_ALGORITHM = _get_default_setting(
        "DEFAULT_HASHING_ALGORITHM"
    )
    MIDDLEWARE: List[str] = global_settings.MIDDLEWARE
    SESSION_CACHE_ALIAS: str = global_settings.SESSION_CACHE_ALIAS
    SESSION_COOKIE_NAME: str = global_settings.SESSION_COOKIE_NAME
    SESSION_COOKIE_AGE: Optional[int] = global_settings.SESSION_COOKIE_AGE
    SESSION_COOKIE_DOMAIN: Optional[str] = global_settings.SESSION_COOKIE_DOMAIN
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
    SESSION_FILE_PATH: types.SESSION_FILE_PATH = global_settings.SESSION_FILE_PATH
    SESSION_SERIALIZER: str = global_settings.SESSION_SERIALIZER
    CACHES: types.CACHES = global_settings.CACHES  # type: ignore
    CACHE_MIDDLEWARE_KEY_PREFIX: str = global_settings.CACHE_MIDDLEWARE_KEY_PREFIX
    CACHE_MIDDLEWARE_SECONDS: Optional[int] = global_settings.CACHE_MIDDLEWARE_SECONDS
    CACHE_MIDDLEWARE_ALIAS: str = global_settings.CACHE_MIDDLEWARE_ALIAS
    AUTH_USER_MODEL: str = global_settings.AUTH_USER_MODEL
    AUTHENTICATION_BACKENDS: List[str] = global_settings.AUTHENTICATION_BACKENDS
    LOGIN_URL: str = global_settings.LOGIN_URL
    LOGIN_REDIRECT_URL: str = global_settings.LOGIN_REDIRECT_URL
    PASSWORD_RESET_TIMEOUT_DAYS: Optional[int] = _get_default_setting(
        "PASSWORD_RESET_TIMEOUT_DAYS"
    )
    PASSWORD_RESET_TIMEOUT: Optional[int] = _get_default_setting(
        "PASSWORD_RESET_TIMEOUT"
    )
    PASSWORD_HASHERS: List[str] = global_settings.PASSWORD_HASHERS
    AUTH_PASSWORD_VALIDATORS: List[dict] = global_settings.AUTH_PASSWORD_VALIDATORS
    SIGNING_BACKEND: str = global_settings.SIGNING_BACKEND
    CSRF_FAILURE_VIEW: str = global_settings.CSRF_FAILURE_VIEW
    CSRF_COOKIE_NAME: str = global_settings.CSRF_COOKIE_NAME
    CSRF_COOKIE_AGE: Optional[int] = global_settings.CSRF_COOKIE_AGE
    CSRF_COOKIE_DOMAIN: Optional[str] = global_settings.CSRF_COOKIE_DOMAIN
    CSRF_COOKIE_PATH: str = global_settings.CSRF_COOKIE_PATH
    CSRF_COOKIE_SECURE: bool = global_settings.CSRF_COOKIE_SECURE
    CSRF_COOKIE_HTTPONLY: bool = global_settings.CSRF_COOKIE_HTTPONLY
    CSRF_COOKIE_SAMESITE: types.CSRF_COOKIE_SAMESITE = _get_default_setting(
        "CSRF_COOKIE_SAMESITE"
    )
    CSRF_HEADER_NAME: str = global_settings.CSRF_HEADER_NAME
    CSRF_TRUSTED_ORIGINS: List[str] = global_settings.CSRF_TRUSTED_ORIGINS
    CSRF_USE_SESSIONS: bool = global_settings.CSRF_USE_SESSIONS
    MESSAGE_STORAGE: str = global_settings.MESSAGE_STORAGE
    LOGGING_CONFIG: str = global_settings.LOGGING_CONFIG
    LOGGING: dict = global_settings.LOGGING
    DEFAULT_EXCEPTION_REPORTER: Optional[str] = _get_default_setting(
        "DEFAULT_EXCEPTION_REPORTER"
    )
    DEFAULT_EXCEPTION_REPORTER_FILTER: str = (
        global_settings.DEFAULT_EXCEPTION_REPORTER_FILTER
    )
    TEST_RUNNER: str = global_settings.TEST_RUNNER
    TEST_NON_SERIALIZED_APPS: List[str] = global_settings.TEST_NON_SERIALIZED_APPS
    FIXTURE_DIRS: types.FIXTURE_DIRS = global_settings.FIXTURE_DIRS
    STATICFILES_DIRS: types.STATICFILES_DIRS = global_settings.STATICFILES_DIRS
    STATICFILES_STORAGE: str = global_settings.STATICFILES_STORAGE
    STATICFILES_FINDERS: List[str] = global_settings.STATICFILES_FINDERS
    MIGRATION_MODULES: Dict[str, str] = global_settings.MIGRATION_MODULES
    SILENCED_SYSTEM_CHECKS: List[str] = global_settings.SILENCED_SYSTEM_CHECKS
    SECURE_BROWSER_XSS_FILTER: Optional[bool] = _get_default_setting(
        "SECURE_BROWSER_XSS_FILTER"
    )
    SECURE_CONTENT_TYPE_NOSNIFF: bool = global_settings.SECURE_CONTENT_TYPE_NOSNIFF
    SECURE_HSTS_INCLUDE_SUBDOMAINS: bool = (
        global_settings.SECURE_HSTS_INCLUDE_SUBDOMAINS
    )
    SECURE_HSTS_PRELOAD: bool = global_settings.SECURE_HSTS_PRELOAD
    SECURE_HSTS_SECONDS: Optional[int] = global_settings.SECURE_HSTS_SECONDS
    SECURE_REDIRECT_EXEMPT: types.SECURE_REDIRECT_EXEMPT = (
        global_settings.SECURE_REDIRECT_EXEMPT
    )
    SECURE_REFERRER_POLICY: types.SECURE_REFERRER_POLICY = _get_default_setting(
        "SECURE_REFERRER_POLICY"
    )
    SECURE_SSL_HOST: Optional[str] = global_settings.SECURE_SSL_HOST
    SECURE_SSL_REDIRECT: bool = global_settings.SECURE_SSL_REDIRECT

    ROOT_URLCONF: Optional[str] = None

    default_database_dsn: Optional[DatabaseDsn] = Field(
        env="DATABASE_URL", configure_database="default"
    )
    default_cache_dsn: Optional[CacheDsn] = Field(
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
                database_dsn: Optional[DatabaseDsn] = values[attr]
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
            cache_dsn: Optional[CacheDsn] = values[attr]
            if cache_dsn:
                CACHES = values.setdefault("CACHES", {})
                CACHES[cache_key] = cache_dsn.to_settings_model()
            del values[attr]
        return values

    @classmethod
    def _get_dsn_fields(cls, field_extra: str) -> Iterable[Tuple[str, str]]:
        field: ModelField
        for field in cls.__fields__.values():
            db_key = field.field_info.extra.get(field_extra)
            if db_key:
                yield db_key, field.name
