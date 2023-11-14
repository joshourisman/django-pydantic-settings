import re
from typing import Any, Dict
from urllib.parse import parse_qs

from django import VERSION
from pydantic import AnyUrl

from pydantic_settings.models import CacheModel

BUILTIN_DJANGO_BACKEND = "django.core.cache.backends.redis.RedisCache"
DJANGO_REDIS_BACKEND = (
    "django_redis.cache.RedisCache" if VERSION[0] < 4 else BUILTIN_DJANGO_BACKEND
)

CACHE_ENGINES = {
    "db": "django.core.cache.backends.db.DatabaseCache",
    "djangopylibmc": "django_pylibmc.memcached.PyLibMCCache",
    "dummy": "django.core.cache.backends.dummy.DummyCache",
    "elasticache": "django_elasticache.memcached.ElastiCache",
    "file": "django.core.cache.backends.filebased.FileBasedCache",
    "hiredis": DJANGO_REDIS_BACKEND,
    "locmem": "django.core.cache.backends.locmem.LocMemCache",
    "memcached": "django.core.cache.backends.memcached.PyLibMCCache",
    "pymemcache": "django.core.cache.backends.memcached.PyMemcacheCache",
    "pymemcached": "django.core.cache.backends.memcached.MemcachedCache",
    "redis-cache": "redis_cache.RedisCache",
    "redis": DJANGO_REDIS_BACKEND,
    "rediss": DJANGO_REDIS_BACKEND,
    "uwsgicache": "uwsgicache.UWSGICache",
}

REDIS_PARSERS = {
    "hiredis": "redis.connection.HiredisParser",
}

FILE_UNIX_PREFIX = (
    "memcached",
    "pymemcached",
    "pymemcache",
    "djangopylibmc",
    "redis",
    "hiredis",
)


class CacheDsn(AnyUrl):
    __slots__ = AnyUrl.__slots__ + ("query_args",)
    host_required = False

    query_args: Dict[str, str]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.query:
            self.query_args = {
                key.upper(): ";".join(val) for key, val in parse_qs(self.query).items()
            }
        else:
            self.query_args = {}

    allowed_schemes = set(CACHE_ENGINES)

    def to_settings_model(self) -> CacheModel:
        return CacheModel(**parse(self))

    @property
    def is_redis_scheme(self) -> bool:
        return self.scheme in ("redis", "rediss", "hiredis")


def parse(dsn: CacheDsn) -> dict:
    """Parses a cache URL."""
    backend = CACHE_ENGINES[dsn.scheme]
    config: dict[str, Any] = {"BACKEND": backend}

    options: dict[str, Any] = {}
    if dsn.scheme in REDIS_PARSERS:
        options["PARSER_CLASS"] = REDIS_PARSERS[dsn.scheme]

    cache_args = dsn.query_args.copy()

    # File based
    if dsn.host is None:
        path = dsn.path or ""

        if dsn.scheme in FILE_UNIX_PREFIX:
            path = "unix:" + path

        if dsn.is_redis_scheme:
            match = re.match(r"(.*)/(\d+)$", path)
            if match:
                path, db = match.groups()
            else:
                db = "0"
            path = f"{path}?db={db}"

        config["LOCATION"] = path
    # Redis URL based
    elif dsn.is_redis_scheme:
        # Specifying the database is optional, use db 0 if not specified.
        db = (dsn.path and dsn.path[1:]) or "0"
        port = dsn.port if dsn.port else 6379
        scheme = "rediss" if dsn.scheme == "rediss" else "redis"
        location = f"{scheme}://{dsn.host}:{port}/{db}"
        if dsn.password:
            if backend == BUILTIN_DJANGO_BACKEND or dsn.scheme == "redis-cache":
                location = location.replace("://", f"://{dsn.password}@", 1)
            else:
                options["PASSWORD"] = dsn.password
        config["LOCATION"] = location

        # Pop redis-cache specific arguments.
        if dsn.scheme == "redis-cache":
            for key in ("PARSER_CLASS", "CONNECTION_POOL_CLASS"):
                if val := cache_args.pop(key, None):
                    options[key] = val

            pool_class_opts = {}
            for pool_class_key in ("MAX_CONNECTIONS", "TIMEOUT"):
                if val := cache_args.pop(pool_class_key, None):
                    pool_class_opts[pool_class_key] = val
            if pool_class_opts:
                options["CONNECTION_POOL_CLASS_KWARGS"] = pool_class_opts

    if dsn.scheme == "uwsgicache":
        config["LOCATION"] = config.get("LOCATION") or "default"

    # Pop special options from cache_args
    # https://docs.djangoproject.com/en/4.0/topics/cache/#cache-arguments
    for key in ["MAX_ENTRIES", "CULL_FREQUENCY"]:
        if val := dsn.query_args.pop(key, None):
            options[key] = int(val)

    config.update(cache_args)
    if options:
        config["OPTIONS"] = options

    return config
