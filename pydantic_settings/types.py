from __future__ import annotations

from re import Pattern
from typing import Callable, Dict, List, Literal, Optional, Tuple, Union

from pydantic import DirectoryPath, EmailStr, IPvAnyAddress

from pydantic_settings.models import CacheModel, DatabaseModel, TemplateBackendModel

EmailList = List[Tuple[str, EmailStr]]
ReferrerOptions = Literal[
    "no-referrer",
    "no-referrer-when-downgrade",
    "origin",
    "origin-when-cross-origin",
    "same-origin",
    "strict-origin",
    "strict-origin-when-cross-origin",
    "unsafe-url",
]
RegexList = List[Pattern[str]]
SameSiteOptions = Literal["Lax", "Strict", "None"]

ABSOLUTE_URL_OVERRIDES = Dict[str, Callable]
ADMINS = Optional[EmailList]
BASE_DIR = Optional[DirectoryPath]
CACHES = Dict[str, CacheModel]
CSRF_COOKIE_SAMESITE = Optional[SameSiteOptions]
DATABASES = Dict[str, DatabaseModel]
DEFAULT_HASHING_ALGORITHM = Optional[Literal["sha1", "sha256"]]
DISALLOWED_USER_AGENTS = RegexList
FILE_UPLOAD_TEMP_DIR = Optional[DirectoryPath]
FIXTURE_DIRS = List[DirectoryPath]
IGNORABLE_404_URLS = RegexList
INTERNAL_IPS = Optional[List[IPvAnyAddress]]
LANGUAGE_COOKIE_SAMESITE = Optional[SameSiteOptions]
LANGUAGES = List[Tuple[str, str]]
LOCALE_PATHS = List[DirectoryPath]
MANAGERS = Optional[EmailList]
SECURE_PROXY_SSL_HEADER = Optional[Tuple[str, str]]
SECURE_REDIRECT_EXEMPT = RegexList
SECURE_REFERRER_POLICY = Optional[ReferrerOptions]
SERVER_EMAIL = Union[EmailStr, Literal["root@localhost"]]
SESSION_COOKIE_SAMESITE = Optional[SameSiteOptions]
SESSION_FILE_PATH = Optional[DirectoryPath]
STATICFILES_DIRS = List[DirectoryPath]
TEMPLATES = List[TemplateBackendModel]
