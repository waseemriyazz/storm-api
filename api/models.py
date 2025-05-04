from pydantic import BaseModel
from typing import Union, Dict, Any
from pydantic import RootModel


class StormRequest(BaseModel):
    topic: str
    stream: bool = False


class StormResponse(BaseModel):
    status_code: int = 200
    data: Union[Dict[str, Any], str]


class ErrorResponse(BaseModel):
    status_code: int
    message: str


class ArticleData(BaseModel):
    article: str


class StormData(RootModel[Union[ArticleData, Dict[str, Any]]]):
    pass
