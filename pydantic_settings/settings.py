from inspect import getsourcefile
from pathlib import Path
from typing import Dict, List, Optional

import dj_database_url
from django.conf import settings
from django.core.management.utils import get_random_secret_key
from pydantic import BaseSettings, DirectoryPath, Field, PyObject, validator

from .database import DatabaseDsn


DEFAULT_SETTINGS_MODULE_FIELD = Field(
    "pydantic_settings.settings.PydanticSettings", env="DJANGO_SETTINGS_MODULE"
)


class SetUp(BaseSettings):
    settings_module: PyObject = DEFAULT_SETTINGS_MODULE_FIELD
    settings_module_string: str = DEFAULT_SETTINGS_MODULE_FIELD

    def configure(self):
        if not settings.configured:
            settings_dict = self.settings_module().dict()

            if settings_dict["BASE_DIR"] is None:
                base_dir = Path(
                    getsourcefile(SetUp().settings_module)
                    or "pydantic_settings.settings.PydanticSettings"
                ).parent.parent.parent
                settings_dict["BASE_DIR"] = base_dir
            else:
                base_dir = settings_dict["BASE_DIR"]

            base_module = self.settings_module_string.rsplit(".", 2)[0]
            if settings_dict["ROOT_URLCONF"] is None:
                settings_dict["ROOT_URLCONF"] = ".".join([base_module, "urls"])
            if settings_dict["WSGI_APPLICATION"] is None:
                settings_dict["WSGI_APPLICATION"] = ".".join([base_module, "wsgi"])

            settings.configure(**settings_dict)


class DatabaseSettings(BaseSettings):
    default: DatabaseDsn = Field(env="DATABASE_URL")

    @validator("*")
    def format_database_settings(cls, v):
        return dj_database_url.parse(v)


class PydanticSettings(BaseSettings):
    BASE_DIR: Optional[DirectoryPath]
    SECRET_KEY: str = Field(default_factory=get_random_secret_key)
    DEBUG: bool = False
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
    ROOT_URLCONF: Optional[str]
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
    WSGI_APPLICATION: Optional[str]
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

    class Config:
        env_prefix = "DJANGO_"
