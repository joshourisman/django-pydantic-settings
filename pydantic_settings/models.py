from typing import List, Optional

from pydantic import DirectoryPath
from pydantic.main import BaseModel
from typing_extensions import TypedDict


class TemplateBackendModel(BaseModel):
    BACKEND: str
    NAME: Optional[str]
    DIRS: Optional[List[DirectoryPath]]
    APP_DIRS: Optional[bool]
    OPTIONS: Optional[dict]


class CacheModel(BaseModel):
    BACKEND: str
    KEY_FUNCTION: Optional[str] = None
    KEY_PREFIX: str = ""
    LOCATION: str = ""
    OPTIONS: dict = {}
    TIMEOUT: Optional[int] = None
    VERSION: int = 1


class DatabateTestDict(TypedDict, total=False):
    CHARSET: Optional[str]
    COLLATION: Optional[str]
    DEPENDENCIES: Optional[List[str]]
    MIGRATE: bool
    MIRROR: Optional[str]
    NAME: Optional[str]
    SERIALIZE: Optional[bool]  # Deprecated since v4.0
    TEMPLATE: Optional[str]
    CREATE_DB: Optional[bool]
    CREATE_USER: Optional[bool]
    USER: Optional[str]
    PASSWORD: Optional[str]
    ORACLE_MANAGED_FILES: Optional[bool]
    TBLSPACE: Optional[str]
    TBLSPACE_TMP: Optional[str]
    DATAFILE: Optional[str]
    DATAFILE_TMP: Optional[str]
    DATAFILE_MAXSIZE: Optional[str]
    DATAFILE_TMP_MAXSIZE: Optional[str]
    DATAFILE_SIZE: Optional[str]
    DATAFILE_TMP_SIZE: Optional[str]
    DATAFILE_EXTSIZE: Optional[str]
    DATAFILE_TMP_EXTSIZE: Optional[str]


class DatabaseModel(BaseModel):
    ATOMIC_REQUESTS: bool = False
    AUTOCOMMIT: bool = True
    ENGINE: str
    HOST: str = ""
    NAME: str = ""
    CONN_MAX_AGE: int = 0
    OPTIONS: dict = {}
    PASSWORD: str = ""
    PORT: str = ""
    TIME_ZONE: Optional[str] = None
    DISABLE_SERVER_SIDE_CURSORS: bool = False
    USER: str = ""
    TEST: DatabateTestDict = {}
    DATA_UPLOAD_MEMORY_MAX_SIZE: Optional[int] = None
