import pytest
from pydantic import BaseModel

from pydantic_settings.cache import CacheDsn


# Do tests against different urls
@pytest.mark.parametrize(
    "url,expected",
    [
        (
            "redis://localhost:6379/0",
            {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": "redis://localhost:6379/0",
            },
        ),
        (
            "rediss://localhost:6379/0?db=1",
            {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": "rediss://localhost:6379/0",
            },
        ),
        (
            "hiredis://:password1@localhost:6379/0?db=1",
            {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": "redis://password1@localhost:6379/0",
                "OPTIONS": {"PARSER_CLASS": "redis.connection.HiredisParser"},
            },
        ),
        (
            "uwsgicache:///some/cache",
            {
                "BACKEND": "uwsgicache.UWSGICache",
                "LOCATION": "/some/cache",
            },
        ),
        (
            "memcached://localhost:11211",
            {"BACKEND": "django.core.cache.backends.memcached.PyLibMCCache"},
        ),
    ],
)
def test_cache_dsn(url, expected):
    class Model(BaseModel):
        url: CacheDsn

    settings_model = Model(url=url).url.to_settings_model()
    assert settings_model.dict(exclude_defaults=True) == expected

    {
        "BACKEND": "django.core.cache.backends.memcached.PyLibMCCache",
    }
