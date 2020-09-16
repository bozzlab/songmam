from pydantic import BaseModel, conlist

from songmam.models.webhook.events.base import (
    WithTimestamp,
    BaseMessaging,
    BaseEvent,
    WithMessaging,
)


class Read(BaseModel):
    watermark: int


class ReadMessaging(BaseMessaging, WithTimestamp):
    read: Read

    @property
    def watermark(self):
        return self.read.watermark


class MessageReadsEvent(BaseEvent, WithMessaging):
    messaging: conlist(ReadMessaging, max_items=1, min_items=1)
