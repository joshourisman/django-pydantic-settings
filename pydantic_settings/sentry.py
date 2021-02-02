from typing import Any

import sentry_sdk
from pydantic import AnyUrl
from pydantic.fields import ModelField
from pydantic.main import BaseConfig
from sentry_sdk.integrations.django import DjangoIntegration

from .settings import Settings


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


class SentrySettings(Settings):
    SENTRY_DSN: SentryDsn
