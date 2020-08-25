from pydantic import BaseModel

from songmam.models.entries.base import MessagingWithTimestamp
from songmam.models import ThingWithId


class Reading(BaseModel):
    watermark: int

class ReadingEntry(MessagingWithTimestamp):
    read: Reading

