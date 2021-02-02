from pathlib import Path
from typing import Dict, List

import dj_database_url
from django.conf import settings
from pydantic import BaseSettings, DirectoryPath, Field, PyObject, validator

from .database import DatabaseDsn


class SetUp(BaseSettings):
    settings_module: PyObject = Field(
        "pydantic_settings.settings.Settings", env="DJANGO_SETTINGS_MODULE"
    )

    def configure(self):
        if not settings.configured:
            settings.configure(**self.settings_module().dict())


class DatabaseSettings(BaseSettings):
    default: DatabaseDsn = Field(env="DATABASE_URL")

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

    class Config:
        env_prefix = "DJANGO_"
