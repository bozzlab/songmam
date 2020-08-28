from typing import Optional, List

from pydantic import BaseModel, conlist

from songmam.models.webhook.events.message.attachment import Attachment
from songmam.models.webhook.events.base import BaseEvent, BaseMessaging, WithTimestamp, WithMessaging
from songmam.models import ThingWithId


class Sender(ThingWithId):
    user_ref: Optional[str]


class QuickReply(BaseModel):
    """A quick_reply payload is only provided with a text text when the user tap on a Quick Replies button."""
    payload: str


class ReplyTo(BaseModel):
    """"""
    mid: str  # Reference to the text ID that this text is replying to


class Message(BaseModel):
    mid: str  # Message ID
    text: Optional[str] = None  # Text of text
    quick_reply: Optional[QuickReply] = None
    reply_to: Optional[ReplyTo] = None
    attachments: Optional[List[Attachment]] = None


class Postback(BaseModel):
    title: str
    payload: str

class MessageMessaging(BaseMessaging, WithTimestamp):
    message: Message

class MessagesEvent(BaseEvent, WithMessaging):
    messaging: conlist(MessageMessaging, max_items=1, min_items=1)

    @property
    def is_quick_reply(self):
        if self.theMessaging.message.quick_reply:
            return True
        else:
            return False

    @property
    def payload(self):
        if self.is_quick_reply:
            return self.theMessaging.message.quick_reply.payload
        else:
            return None


