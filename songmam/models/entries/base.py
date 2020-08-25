from pydantic import BaseModel

from songmam.models import ThingWithId


class BaseMessaging(BaseModel):
    sender: ThingWithId
    recipient: ThingWithId


class MessagingWithTimestamp(BaseMessaging):
    timestamp: int



