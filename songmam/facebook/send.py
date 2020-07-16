# https://developers.facebook.com/docs/messenger-platform/send-messages#send_api_basics
from enum import auto

from pydantic import BaseModel
from typing import Optional

from songmam.utils import AutoName


class MessageTag(AutoName):
    """https://developers.facebook.com/docs/messenger-platform/send-messages/message-tags"""
    CONFIRMED_EVENT_UPDATE = auto()
    POST_PURCHASE_UPDATE = auto()
    ACCOUNT_UPDATE = auto()
    HUMAN_AGENT = auto()


class SendResponse(BaseModel):
    recipient_id: Optional[str]
    message_id: str
