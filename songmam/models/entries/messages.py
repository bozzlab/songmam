from typing import Optional, List, Union

from pydantic import BaseModel, validator, conlist

from songmam.models.entries.message.attachment import Attachment
from songmam.models.entries.base import WithTimestamp, AlmostBaseEntity
from songmam.models import ThingWithId


class Sender(ThingWithId):
    user_ref: Optional[str]


class QuickReply(BaseModel):
    """A quick_reply payload is only provided with a text message when the user tap on a Quick Replies button."""
    payload: str


class ReplyTo(BaseModel):
    """"""
    mid: str  # Reference to the message ID that this message is replying to


class Message(BaseModel):
    mid: str  # Message ID
    text: Optional[str] = None  # Text of message
    quick_reply: Optional[QuickReply] = None
    reply_to: Optional[ReplyTo] = None
    attachments: Optional[List[Attachment]] = None


class Postback(BaseModel):
    title: str
    payload: str


class Messaging(WithTimestamp):
    sender: Sender
    message: Message

class EntityWithMessaging(BaseModel):
    messaging: conlist(Messaging, min_items=1, max_items=1)

    @property
    def theMessaging(self):
        return self.messaging[0]

    @property
    def sender(self):
        return self.theMessaging.sender

    @property
    def recipient(self):
        return self.theMessaging.recipient

    @property
    def is_quick_reply(self):
        if self.theMessaging.message.quick_reply:
            return True
        else:
            return False

class MessageEntry(AlmostBaseEntity, EntityWithMessaging):
    pass

