from typing import List

from pydantic import BaseModel, conlist

from songmam.models.entries.base import WithTimestamp
from songmam.models.entries.messages import MessageEntry


class Delivery(BaseModel):
    mids: List[str]
    watermark: int


class Deliveries(WithTimestamp):
    delivery: Delivery

class DeliveriesEntry(MessageEntry):
    messaging: conlist(Deliveries, min_items=1, max_items=1)

    @property
    def mids(self):
        return self.theMessaging.delivery.mids

    @property
    def watermark(self):
        return self.theMessaging.delivery.watermark
"""
https://developers.facebook.com/docs/messenger-platform/reference/webhook-events/message-deliveries
"""
