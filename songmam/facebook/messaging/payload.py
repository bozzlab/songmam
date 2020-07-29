"""
Payload is final data  form ready to use with request api
"""
from enum import auto
from typing import List, Union, Optional, Any

from pydantic import BaseModel, validator, conlist

from songmam.facebook import ThingWithId
from songmam.facebook.entries.messages import Sender
from songmam.facebook.messaging.message_tags import MessageTag
from songmam.facebook.messaging.messaging_type import MessagingType
from songmam.facebook.messaging.notification_type import NotificationType
from songmam.facebook.messaging.sender_action import SenderAction
from songmam.facebook.messaging.templates.button import AllButtonTypes
from songmam.facebook.messaging.templates import Message
from songmam.facebook.send import SendRecipient


class CompletePayload(BaseModel):
    recipient: Union[SendRecipient, Sender, ThingWithId]
    template_type: Optional[str] = None
    message: Optional[Message]
    messaging_type: Optional[MessagingType] = MessagingType.RESPONSE
    tag: Optional[MessageTag]
    notification_type: Optional[NotificationType] = NotificationType.REGULAR

    persona_id: Optional[str] = None


class SenderActionPayload(CompletePayload):
    sender_action: SenderAction

class SendingQuickRepliesEntry(CompletePayload):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/buttons/quick-replies
    """
    message: Any
    buttons: conlist(AllButtonTypes, max_items=3, min_items=1)  # Set of 1-3 buttons that appear as call-to-actions.



from songmam.utils import AutoNameLower


class SenderAction(AutoNameLower):
    """https://developers.facebook.com/docs/messenger-platform/send-messages/sender-actions"""
    TYPING_ON = auto()
    TYPING_OFF = auto()
    MARK_SEEN = auto()


