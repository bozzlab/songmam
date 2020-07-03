from typing import Optional, List

from pydantic import BaseModel

from songmam.events.attachment import Attachment
from songmam.events.base import MessagingWithTimestamp, ThingWithID


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

class TextMessage(MessagingWithTimestamp):
    sender: Sender
    message: Message

