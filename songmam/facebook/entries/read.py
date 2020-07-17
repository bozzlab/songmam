from pydantic import BaseModel

from songmam.facebook.entries.base import MessagingWithTimestamp
from songmam.facebook import ThingWithId


class Reading(BaseModel):
    watermark: int

class ReadingEntry(MessagingWithTimestamp):
    read: Reading

