import json
from pathlib import Path

import pytest
from django.conf import settings
from django.test import Client
from django.utils.functional import empty

from pydantic_settings import SetUp


@pytest.fixture()
def configure_settings(monkeypatch):
    settings._wrapped = empty

    def func(env: dict = {}):
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        SetUp().configure()

    yield func
    settings._wrapped = empty


def test_no_env(configure_settings):
    """Test that Django can run with no settings specified in the environment."""
    configure_settings()

    assert settings.DATABASES == {}


def test_env_loaded(configure_settings):
    configure_settings({"DATABASE_URL": "sqlite:///foo"})

    assert settings.DATABASES["default"]["NAME"] == "foo"


def test_env_loaded2(configure_settings):
    configure_settings({"DATABASE_URL": "sqlite:///bar"})
    assert settings.DATABASES["default"]["NAME"] == "bar"


def test_sqlite_path(configure_settings):
    """
    Make sure we aren't improperly stripping the leading slash from the path for SQLite databases with an
    absolute path
    """
    configure_settings({"DATABASE_URL": "sqlite:////db/test.db"})

    assert settings.DATABASES["default"]["NAME"] == "/db/test.db"


def test_database_port(configure_settings):
    configure_settings({"DATABASE_URL": "postgres://foo:bar@foo.com:6543/database"})

    assert settings.DATABASES["default"]["PORT"] == "6543"


def test_multiple_databases(configure_settings):
    configure_settings(
        {
            "DJANGO_SETTINGS_MODULE": "settings_test.database_settings.TestSettings",
            "DATABASE_URL": "postgres://foo:bar@foo.com:6543/database",
            "SECONDARY_DATABASE_URL": "sqlite:///secondary.db",
        }
    )

    assert "default" in settings.DATABASES
    assert "secondary" in settings.DATABASES


def test_allowed_hosts(configure_settings):
    configure_settings(
        {"DJANGO_ALLOWED_HOSTS": '["*", "127.0.0.1", ".localhost", "[::1]"]'}
    )

    assert settings.DEBUG is False


def test_language_cookie_path(configure_settings):
    configure_settings({"DJANGO_LANGUAGE_COOKIE_PATH": "/foo/bar"})

    assert settings.LANGUAGE_COOKIE_PATH == "/foo/bar"


def test_email_host_password(configure_settings):
    configure_settings({"DJANGO_EMAIL_HOST_PASSWORD": "password1"})

    assert settings.EMAIL_HOST_PASSWORD == "password1"


def test_templates_settings(configure_settings):
    configure_settings(
        {
            "DJANGO_TEMPLATES": json.dumps(
                [
                    {
                        "BACKEND": "django.template.backends.django.DjangoTemplates",
                        "APP_DIRS": True,
                    }
                ]
            )
        }
    )

    assert (
        settings.TEMPLATES[0]["BACKEND"]
        == "django.template.backends.django.DjangoTemplates"
    )


def test_base_dir(configure_settings):
    configure_settings({"DJANGO_BASE_DIR": "settings_test"})

    assert settings.BASE_DIR == Path("settings_test")
    assert settings.ROOT_URLCONF == "settings_test.urls"
    assert settings.WSGI_APPLICATION == "settings_test.wsgi.application"


def test_http(configure_settings):
    configure_settings({"DJANGO_BASE_DIR": "settings_test", "DJANGO_DEBUG": "True"})

    client = Client()
    response = client.get("/")

    assert response.json()["success"] is True


def test_escaped_gcp_cloudsql_socket(configure_settings):
    configure_settings(
        {
            "DJANGO_BASE_DIR": "settings_test",
            "DATABASE_URL": "postgres://username:password@%2Fcloudsql%2Fproject%3Aregion%3Ainstance/database",
        }
    )

    # assert "default" in settings.DATABASES

    default = settings.DATABASES["default"]
    assert default["NAME"] == "database"
    assert default["USER"] == "username"
    assert default["PASSWORD"] == "password"
    assert default["HOST"] == "/cloudsql/project:region:instance"
    assert default["ENGINE"] == "django.db.backends.postgresql"


from django.conf import global_settings

gd = global_settings.DATABASES


def test_unescaped_gcp_cloudsql_socket(configure_settings):
    configure_settings(
        {
            "DJANGO_BASE_DIR": "settings_test",
            "DATABASE_URL": "postgres://username:password@/cloudsql/project:region:instance/database",
        }
    )

    assert "default" in settings.DATABASES

    default = settings.DATABASES["default"]
    assert default["NAME"] == "database"
    assert default["USER"] == "username"
    assert default["PASSWORD"] == "password"
    assert default["HOST"] == "/cloudsql/project:region:instance"
    assert default["ENGINE"] == "django.db.backends.postgresql"


def test_default_db(configure_settings):
    base_dir = Path(__file__).parent
    configure_settings(
        {
            "DJANGO_SETTINGS_MODULE": "settings_test.database_settings.TestDefaultSettings",
            "DJANGO_BASE_DIR": base_dir,
        }
    )

    default = settings.DATABASES["default"]
    assert default["NAME"] == str(base_dir / "db.sqlite3")


def test_default_db_no_basedir(configure_settings):
    configure_settings(
        {
            "DJANGO_SETTINGS_MODULE": "pydantic_settings.default.DjangoDefaultProjectSettings",
        }
    )

    default = settings.DATABASES["default"]
    assert default["NAME"] == "db.sqlite3"
