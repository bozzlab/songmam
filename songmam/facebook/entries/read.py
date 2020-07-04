from pydantic import BaseModel

from songmam.facebook.entries.base import MessagingWithTimestamp, ThingWithID


class Reading(BaseModel):
    watermark: int

class ReadingEnry(MessagingWithTimestamp):
    read: Reading

