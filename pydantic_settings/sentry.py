from typing import Any

import sentry_sdk
from pydantic import AnyUrl
from pydantic.config import BaseConfig
from pydantic.fields import ModelField
from sentry_sdk.integrations.django import DjangoIntegration

from .settings import PydanticSettings


class SentryDsn(AnyUrl):
    @classmethod
    def validate(cls, value: Any, field: ModelField, config: BaseConfig) -> AnyUrl:
        dsn = super().validate(value, field, config)

        sentry_sdk.init(
            dsn=dsn,
            integrations=[DjangoIntegration()],
            traces_sample_rate=1.0,
            send_default_pii=True,
        )

        return dsn


class SentrySettings(PydanticSettings):
    SENTRY_DSN: SentryDsn
