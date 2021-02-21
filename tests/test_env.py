import json
import os
from unittest.mock import patch

from django.conf import settings
from django.utils.functional import empty
from pydantic_settings import SetUp


@patch.dict(os.environ, clear=True, DATABASE_URL="sqlite:///foo")
def test_env_loaded():
    SetUp().configure()

    assert settings.DATABASES["default"]["NAME"] == "foo"


@patch.dict(os.environ, clear=True, DATABASE_URL="sqlite:///bar")
def test_env_loaded2():
    settings._wrapped = empty
    SetUp().configure()

    assert settings.DATABASES["default"]["NAME"] == "bar"


@patch.dict(
    os.environ,
    clear=True,
    DJANGO_ALLOWED_HOSTS='["*", "127.0.0.1", ".localhost", "[::1]"]',
    DATABASE_URL="sqlite:///bar",
)
def test_allowed_hosts():
    settings._wrapped = empty
    SetUp().configure()

    assert settings.DEBUG is False


@patch.dict(
    os.environ,
    clear=True,
    DJANGO_LANGUAGE_COOKIE_PATH="/foo/bar",
    DATABASE_URL="sqlite:///foo",
)
def test_language_cookie_path():
    settings._wrapped = empty
    SetUp().configure()

    assert settings.LANGUAGE_COOKIE_PATH == "/foo/bar"


@patch.dict(
    os.environ,
    clear=True,
    DJANGO_EMAIL_HOST_PASSWORD="password1",
    DATABASE_URL="sqlite:///foo",
)
def test_email_host_password():
    settings._wrapped = empty
    SetUp().configure()

    assert settings.EMAIL_HOST_PASSWORD == "password1"


@patch.dict(
    os.environ,
    clear=True,
    DJANGO_TEMPLATES=json.dumps(
        [
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "APP_DIRS": True,
            }
        ]
    ),
    DATABASE_URL="sqlite:///foo",
)
def test_templates_settings():
    settings._wrapped = empty
    SetUp().configure()

    assert (
        settings.TEMPLATES[0]["BACKEND"]
        == "django.template.backends.django.DjangoTemplates"
    )
