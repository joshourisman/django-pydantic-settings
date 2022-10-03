from typing import Optional

from pydantic import Field

from pydantic_settings import PydanticSettings
from pydantic_settings.database import DatabaseDsn
from pydantic_settings.default import DjangoDefaultProjectSettings


class TestSettings(PydanticSettings):
    secondary_database_dsn: Optional[DatabaseDsn] = Field(
        env="SECONDARY_DATABASE_URL", configure_database="secondary"
    )


class TestDefaultSettings(DjangoDefaultProjectSettings):
    ROOT_URLCONF = "tests.settings_test.urls"


class TestDotenvSettings(PydanticSettings):
    STATIC_URL = "/static-from-settings/"
    MEDIA_URL = "/media-from-settings/"

    class Config:
        env_file = ".env"


if __name__ == "__main__":
    # Run this file directly with DATABASE_URL and/or SECONDARY_DATABASE_URL environment
    # variables to test the database settings.
    settings = TestSettings()
    import pprint

    pprint.pprint(settings.dict(exclude_defaults=True).get("DATABASES"))
