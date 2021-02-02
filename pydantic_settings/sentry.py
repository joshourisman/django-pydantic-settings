import sentry_sdk
from pydantic import AnyUrl
from sentry_sdk.integrations.django import DjangoIntegration

from .settings import Settings


class SentryDsn(AnyUrl):
    @classmethod
    def validate(cls, *args, **kwargs) -> AnyUrl:
        dsn = super().validate(*args, **kwargs)

        sentry_sdk.init(
            dsn=dsn,
            integrations=[DjangoIntegration()],
            traces_sample_rate=1.0,
            send_default_pii=True,
        )

        return dsn


class SentrySettings(Settings):
    SENTRY_DSN: SentryDsn
