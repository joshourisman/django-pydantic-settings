from typing import Dict, List, Optional

from pydantic import DirectoryPath
from pydantic.main import BaseModel

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


class TemplateBackendModel(BaseModel):
    BACKEND: str
    NAME: Optional[str]
    DIRS: Optional[List[DirectoryPath]]
    APP_DIRS: Optional[bool]
    OPTIONS: Optional[dict]


class CacheBackendModel(BaseModel):
    default: Dict[Literal["BACKEND"], str]
