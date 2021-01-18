import os
from pathlib import Path

from configurations import Configuration, values


class Base(Configuration):
    BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
    DEBUG = False
    SECRET_KEY = values.SecretValue()
    ALLOWED_HOSTS = ["*"]

    INSTALLED_APPS = (
        ["whitenoise.runserver_nostatic"]
        + [
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.messages",
            "django.contrib.sessions",
            "django.contrib.staticfiles",
        ]
        + ["django_extensions"]
        + []
    )

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

    ROOT_URLCONF = "settings_test.urls"

    TEMPLATES = [
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

    WSGI_APPLICATION = "settings_test.wsgi.application"

    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
        {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
        {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
    ]

    LANGUAGE_CODE = "en-us"
    TIME_ZONE = "US/Eastern"
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True

    STATIC_URL = "/static/"
    STATIC_ROOT = os.path.join(BASE_DIR, "static")

    SITE_ID = 1

    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
