from pydantic import BaseSettings, Field
from pydantic_settings import PydanticSettings
from pydantic_settings.settings import DatabaseSettings
from pydantic_settings.database import DatabaseDsn


class Databases(DatabaseSettings):
    default: DatabaseDsn = Field(env="DATABASE_URL")
    secondary: DatabaseDsn = Field(env="SECONDARY_DATABASE_URL")


class TestSettings(PydanticSettings):
    DATABASES: Databases = Field({})
