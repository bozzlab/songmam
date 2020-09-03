from typing import Optional, List
from typing import Union

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
    reply_to: Optional[ReplyTo] = None
    attachments: Optional[List[Attachment]] = None

    @property
    def is_quick_reply(self):
        return False

class WithQuickReply(BaseModel):
    quick_reply: QuickReply

    @property
    def is_quick_reply(self):
        return True

    @property
    def payload(self):
        return self.quick_reply.payload

class MessageWithQuickReply(Message, WithQuickReply):
    pass

class Postback(BaseModel):
    title: str
    payload: str

class MessageMessaging(BaseMessaging, WithTimestamp):
    message: Message

class MessageMessagingWithQuickReply(BaseMessaging, WithTimestamp):
    message: MessageWithQuickReply

class UnifiedMessagesEvent(BaseEvent, WithMessaging):
    messaging: conlist(Union[MessageMessaging, MessageWithQuickReply], max_items=1, min_items=1)

    @property
    def is_quick_reply(self):
        return self.theMessaging.message.is_quick_reply

    @property
    def payload(self):
        if self.is_quick_reply:
            return self.theMessaging.message.payload
        else:
            return None

class MessagesEvent(UnifiedMessagesEvent):
    """
    Without QuickReply
    """
    messaging: conlist(MessageMessaging, max_items=1, min_items=1)



class MessagesEventWithQuickReply(UnifiedMessagesEvent):
    """
        With QuickReply
    """
    messaging: conlist(MessageMessagingWithQuickReply, max_items=1, min_items=1)