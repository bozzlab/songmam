from typing import List

from pydantic import BaseModel, conlist

from songmam.facebook.entries.base import MessagingWithTimestamp
from songmam.facebook.entries.messages import MessageEntry


class Delivery(BaseModel):
    mids: List[str]
    watermark: int


class DeliveriesMessaging(MessagingWithTimestamp):
    delivery: Delivery

class DeliveriesEntry(MessageEntry):
    messaging: conlist(DeliveriesMessaging, min_items=1, max_items=1)

"""
https://developers.facebook.com/docs/messenger-platform/reference/webhook-events/message-deliveries
"""
