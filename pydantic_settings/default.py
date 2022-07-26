from pydantic_settings.database import DatabaseSettings
from pydantic_settings.models import TemplateBackendModel
from pydantic_settings.settings import PydanticSettings


class DjangoDefaultProjectSettings(PydanticSettings):
    """
    An example of a PydanticSettings subclass that uses the default settings Django
    generates for new projects.
    """

    DATABASES: DatabaseSettings = DatabaseSettings.parse_obj(
        {"default": "sqlite:///db.sqlite3"}
    )

    TEMPLATES: list[TemplateBackendModel] = [
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

    INSTALLED_APPS: list[str] = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    ]

    MIDDLEWARE: list[str] = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

    AUTH_PASSWORD_VALIDATORS: list[dict] = [
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
