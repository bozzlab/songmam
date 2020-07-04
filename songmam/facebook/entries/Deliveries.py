from typing import List

from pydantic import BaseModel

from songmam.facebook.entries.base import Messaging

class Delivery(BaseModel):
    mids: List[str]
    watermark: int

class DeliveriesEntry(Messaging):
    delivery: Delivery

