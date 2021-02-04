from django.conf import settings
from pydantic_settings import SetUp


def test_env_loaded():
    SetUp().configure()

    assert settings.DATABASES["default"]["NAME"] == "db"
