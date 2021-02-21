import os
from unittest.mock import patch

from django.conf import settings
from django.utils.functional import empty
from pydantic_settings import SetUp


def test_no_env():
    """Test that Django can run with no settings specified in the environment."""
    settings._wrapped = empty
    SetUp().configure()

    assert settings.DATABASES == {}


@patch.dict(os.environ, clear=True, DATABASE_URL="sqlite:///foo")
def test_env_loaded():
    settings._wrapped = empty
    SetUp().configure()

    assert settings.DATABASES["default"]["NAME"] == "foo"


@patch.dict(os.environ, clear=True, DATABASE_URL="sqlite:///bar")
def test_env_loaded2():
    settings._wrapped = empty
    SetUp().configure()

    assert settings.DATABASES["default"]["NAME"] == "bar"
