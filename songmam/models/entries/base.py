from pydantic import BaseModel, conlist

from songmam.models import ThingWithId


class BaseMessaging(BaseModel):
    sender: ThingWithId
    recipient: ThingWithId


class WithTimestamp(BaseMessaging):
    timestamp: int

class AlmostBaseEntity(BaseModel):
    id: str
    time: int