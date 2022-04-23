from pydantic import BaseSettings, Field
from pydantic_settings import PydanticSettings
from pydantic_settings.database import DatabaseDsn


class DatabaseSettings(BaseSettings):
    DEFAULT: DatabaseDsn = Field(env="DATABASE_URL")
    SECONDARY: DatabaseDsn = Field(env="SECONDARY_DATABASE_URL")


class TestSettings(PydanticSettings):
    DATABASES: DatabaseSettings = Field({})
