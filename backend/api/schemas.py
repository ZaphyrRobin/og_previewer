from database.enums import URLStatus
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import HttpUrl
from typing import List
from typing import Optional


class URLSubmit(BaseModel):
    url: str


class URLInfo(BaseModel):
    id: int
    url: HttpUrl
    image_url: Optional[str]
    status: URLStatus

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class PaginatedURLInfo(BaseModel):
    results: List[URLInfo]
    next_cursor: Optional[int]

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
