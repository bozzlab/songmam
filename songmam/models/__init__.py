from pydantic import BaseModel


class ThingWithId(BaseModel):
    id: str