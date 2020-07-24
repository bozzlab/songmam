from pydantic import BaseModel

from songmam.facebook import ThingWithId


class BaseMessaging(BaseModel):
    sender: ThingWithId
    recipient: ThingWithId


class MessagingWithTimestamp(BaseModel):
    sender: ThingWithId
    recipient: ThingWithId
    timestamp: int



