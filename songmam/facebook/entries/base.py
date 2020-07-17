from pydantic import BaseModel

from songmam.facebook import ThingWithID


class Messaging(BaseModel):
    sender: ThingWithID
    recipient: ThingWithID


class MessagingWithTimestamp(BaseModel):
    sender: ThingWithID
    recipient: ThingWithID
    timestamp: int



