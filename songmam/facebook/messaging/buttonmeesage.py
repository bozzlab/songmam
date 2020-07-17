"""
Payload is final data  form ready to use with request api
"""
from enum import auto
from typing import List, Union, Optional, Any

from pydantic import BaseModel, validator

from songmam.facebook import ThingWithId
from songmam.facebook.entries.messages import Sender
from songmam.facebook.messaging.message_tags import MessageTag
from songmam.facebook.messaging.messaging_type import MessagingType
from songmam.facebook.messaging.notification_type import NotificationType
from songmam.facebook.messaging import SenderAction
from songmam.facebook.messaging.templates.button import URLButton, PostbackButton, CallButton, LogInButton, \
    LogOutButton, GamePlayButton
from songmam.facebook.messaging.templates import Message
from songmam.facebook.send import SendRecipient

ButtonTypeList = Union[URLButton, PostbackButton, CallButton, LogInButton, LogOutButton, GamePlayButton]

class BasePayload(BaseModel):
    template_type: Optional[str] = None
    recipient: Union[SendRecipient, Sender, ThingWithId]
    message: Optional[Message]
    messaging_type: Optional[MessagingType] = MessagingType.RESPONSE
    tag: Optional[MessageTag]
    notification_type: Optional[NotificationType] = NotificationType.REGULAR


class SenderActionPayload(BasePayload):
    sender_action: SenderAction

class SendingQuickRepliesEntry(BasePayload):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/buttons/quick-replies
    """
    message: Any
    buttons: List[ButtonTypeList]  # Set of 1-3 buttons that appear as call-to-actions.

    @validator('buttons')
    def buttons_limit_to_3_buttons(cls, v):
        if len(v) > 3:
            raise ValueError('Maximum 3 buttons for Button Template.')
        elif len(v) == 0:
            raise ValueError('Set at least 1 button for Button Template.')
        return v




from songmam.utils import AutoNameLower


class SenderAction(AutoNameLower):
    """https://developers.facebook.com/docs/messenger-platform/send-messages/sender-actions"""
    TYPING_ON = auto()
    TYPING_OFF = auto()
    MARK_SEEN = auto()


