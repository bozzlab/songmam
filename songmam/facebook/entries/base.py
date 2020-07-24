from pydantic import BaseModel

from songmam.facebook import ThingWithId


class BaseMessaging(BaseModel):
    sender: ThingWithId
    recipient: ThingWithId


class MessagingWithTimestamp(BaseMessaging):
    timestamp: int



