from pydantic import BaseModel


class ThingWithID(BaseModel):
    id: str



class Messaging(BaseModel):
    sender: ThingWithID
    recipient: ThingWithID

class MessagingWithTimestamp(BaseModel):
    sender: ThingWithID
    recipient: ThingWithID
    timestamp: int