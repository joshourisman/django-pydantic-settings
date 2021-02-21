from inspect import getsourcefile
from pathlib import Path
from typing import Dict, List, Optional

import dj_database_url
from django.conf import global_settings, settings
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
            else:
                base_dir = settings_dict["BASE_DIR"]

            base_module = self.settings_module_string.rsplit(".", 2)[0]
            if settings_dict["ROOT_URLCONF"] is None:
                settings_dict["ROOT_URLCONF"] = ".".join([base_module, "urls"])
            if settings_dict.get("WSGI_APPLICATION") is None:
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
    DEBUG: Optional[bool]
    ALLOWED_HOSTS: Optional[List[str]] = global_settings.ALLOWED_HOSTS
    INSTALLED_APPS: Optional[List[str]] = global_settings.INSTALLED_APPS
    MIDDLEWARE: Optional[List[str]] = global_settings.MIDDLEWARE
    ROOT_URLCONF: Optional[str]
    TEMPLATES: Optional[List[Dict]] = global_settings.TEMPLATES
    WSGI_APPLICATION: Optional[str]
    DATABASES: DatabaseSettings = Field({})
    AUTH_PASSWORD_VALIDATORS: Optional[
        List[Dict[str, str]]
    ] = global_settings.AUTH_PASSWORD_VALIDATORS
    LANGUAGE_CODE: Optional[str] = global_settings.LANGUAGE_CODE
    TIME_ZONE: Optional[str] = global_settings.TIME_ZONE
    USE_I18N: Optional[bool] = global_settings.USE_I18N
    USE_L10N: Optional[bool] = global_settings.USE_L10N
    USE_TZ: Optional[bool] = global_settings.USE_TZ
    STATIC_URL: Optional[str] = global_settings.STATIC_URL

    class Config:
        env_prefix = "DJANGO_"
