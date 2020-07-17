from typing import Optional, List, Union

from pydantic import BaseModel, validator

from songmam.facebook.entries.echo import EchoEntry
from songmam.facebook.entries.handovers import HandoversEntry

from songmam.facebook.entries.message.attachment import Attachment
from songmam.facebook.entries.base import MessagingWithTimestamp
from songmam.facebook import ThingWithID
from songmam.facebook.messaging.templates.button import PostbackButton


class Sender(ThingWithID):
    user_ref: Optional[str]

class QuickReply(BaseModel):
    """A quick_reply payload is only provided with a text message when the user tap on a Quick Replies button."""
    payload: str

class ReplyTo(BaseModel):
    """"""
    mid: str # Reference to the message ID that this message is replying to

class Message(BaseModel):
    mid: str  # Message ID
    text: Optional[str]  # Text of message
    quick_reply: Optional[QuickReply]
    reply_to: Optional[ReplyTo]
    attachments: Optional[List[Attachment]]

class Postback(BaseModel):
    title: str
    payload: str

class Messaging(MessagingWithTimestamp):
    sender: Sender
    message: Optional[Message]
    postback: Optional[Postback]


class MessageEntry(BaseModel):
    id: str
    time: int
    messaging: List[Messaging]

    @property
    def theMessaging(self):
        return self.messaging[0]

    @validator('messaging')
    def messaging_must_has_one_and_only_one_element(cls, v):
        assert len(v) == 1
        return v