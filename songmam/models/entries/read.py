from pydantic import BaseModel

from songmam.models.entries.base import WithTimestamp
from songmam.models import ThingWithId


class Reading(BaseModel):
    watermark: int

class ReadingEntry(WithTimestamp):
    read: Reading

    @property
    def watermark(self):
        return self.read.watermark

