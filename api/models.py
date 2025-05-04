from pydantic import BaseModel


class StormRequest(BaseModel):
    topic: str
    stream: bool = False
