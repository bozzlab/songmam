from pydantic import BaseModel


class ThingWithID(BaseModel):
    id: str