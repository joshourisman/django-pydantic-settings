import os
from unittest.mock import patch

from django.conf import settings
from pydantic_settings import SetUp


@patch.dict(os.environ, clear=True, DATABASE_URL="sqlite:///db")
def test_env_loaded():
    SetUp().configure()

    assert settings.DATABASES["default"]["NAME"] == "db"
