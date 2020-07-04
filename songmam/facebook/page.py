from pydantic import BaseModel


class Me(BaseModel):
    id: str
    name: str

