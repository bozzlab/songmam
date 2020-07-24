from typing import List

from pydantic import BaseModel

from songmam.facebook.entries.base import BaseMessaging


class Delivery(BaseModel):
    mids: List[str]
    watermark: int


class DeliveriesEntry(BaseMessaging):
    delivery: Delivery


"""
https://developers.facebook.com/docs/messenger-platform/reference/webhook-events/message-deliveries
"""
