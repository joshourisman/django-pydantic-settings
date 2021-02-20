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
