from typing import Dict, List

from pydantic import root_validator

from pydantic_settings.models import DatabaseModel, TemplateBackendModel
from pydantic_settings.settings import DatabaseModel, PydanticSettings


class DjangoDefaultProjectSettings(PydanticSettings):
    """
    An example of a PydanticSettings subclass that uses the default settings Django
    generates for new projects.
    """

    DATABASES: Dict[str, DatabaseModel] = {"default": "sqlite:///db.sqlite3"}  # type: ignore

    TEMPLATES: List[TemplateBackendModel] = [
        TemplateBackendModel.parse_obj(data)
        for data in [
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
    ]

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

    AUTH_PASSWORD_VALIDATORS: List[dict] = [
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

    TIME_ZONE: str = "UTC"
    USE_TZ: bool = True

    STATIC_URL: str = "static/"

    DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"

    @root_validator(allow_reuse=True)
    def default_database(cls, values):
        base_dir = values.get("BASE_DIR")
        if base_dir:
            values["DATABASES"]["default"] = DatabaseModel(
                ENGINE="django.db.backends.sqlite3", NAME=str(base_dir / "db.sqlite3")
            )
        return values
