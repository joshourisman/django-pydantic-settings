import json
from pathlib import Path

from django.conf import settings
from django.test import Client
from django.utils.functional import empty
from pydantic_settings import SetUp


def test_no_env():
    """Test that Django can run with no settings specified in the environment."""
    settings._wrapped = empty
    SetUp().configure()

    assert settings.DATABASES == {}


def test_env_loaded(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///foo")
    settings._wrapped = empty
    SetUp().configure()

    assert settings.DATABASES["default"]["NAME"] == "foo"


def test_env_loaded2(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///bar")
    settings._wrapped = empty
    SetUp().configure()

    assert settings.DATABASES["default"]["NAME"] == "bar"


def test_allowed_hosts(monkeypatch):
    monkeypatch.setenv(
        "DJANGO_ALLOWED_HOSTS", '["*", "127.0.0.1", ".localhost", "[::1]"]'
    )
    settings._wrapped = empty
    SetUp().configure()

    assert settings.DEBUG is False


def test_language_cookie_path(monkeypatch):
    monkeypatch.setenv("DJANGO_LANGUAGE_COOKIE_PATH", "/foo/bar")
    settings._wrapped = empty
    SetUp().configure()

    assert settings.LANGUAGE_COOKIE_PATH == "/foo/bar"


def test_email_host_password(monkeypatch):
    monkeypatch.setenv("DJANGO_EMAIL_HOST_PASSWORD", "password1")
    settings._wrapped = empty
    SetUp().configure()

    assert settings.EMAIL_HOST_PASSWORD == "password1"


def test_templates_settings(monkeypatch):
    monkeypatch.setenv(
        "DJANGO_TEMPLATES",
        json.dumps(
            [
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "APP_DIRS": True,
                }
            ]
        ),
    )
    settings._wrapped = empty
    SetUp().configure()

    assert (
        settings.TEMPLATES[0]["BACKEND"]
        == "django.template.backends.django.DjangoTemplates"
    )


def test_base_dir(monkeypatch):
    monkeypatch.setenv("DJANGO_BASE_DIR", "settings_test")

    settings._wrapped = empty
    SetUp().configure()

    assert settings.BASE_DIR == Path("settings_test")
    assert settings.ROOT_URLCONF == "settings_test.urls"
    assert settings.WSGI_APPLICATION == "settings_test.wsgi.application"


def test_http(monkeypatch):
    monkeypatch.setenv("DJANGO_BASE_DIR", "settings_test")
    monkeypatch.setenv("DJANGO_DEBUG", "True")

    settings._wrapped = empty
    SetUp().configure()

    client = Client()
    response = client.get("/")

    assert response.json()["success"] is True


def test_escaped_gcp_cloudsql_socket(monkeypatch):
    monkeypatch.setenv("DJANGO_BASE_DIR", "settings_test")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgres://username:password@%2Fcloudsql%2Fproject%3Aregion%3Ainstance/database",
    )

    settings._wrapped = empty
    SetUp().configure()

    assert "default" in settings.DATABASES

    default = settings.DATABASES["default"]
    assert default["NAME"] == "database"
    assert default["USER"] == "username"
    assert default["PASSWORD"] == "password"
    assert default["HOST"] == "/cloudsql/project:region:instance"
    assert default["ENGINE"] == "django.db.backends.postgresql_psycopg2"


def test_unescaped_gcp_cloudsql_socket(monkeypatch):
    monkeypatch.setenv("DJANGO_BASE_DIR", "settings_test")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgres://username:password@/cloudsql/project:region:instance/database",
    )

    settings._wrapped = empty
    SetUp().configure()

    assert "default" in settings.DATABASES

    default = settings.DATABASES["default"]
    assert default["NAME"] == "database"
    assert default["USER"] == "username"
    assert default["PASSWORD"] == "password"
    assert default["HOST"] == "/cloudsql/project:region:instance"
    assert default["ENGINE"] == "django.db.backends.postgresql_psycopg2"
