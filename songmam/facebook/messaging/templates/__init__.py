from typing import Literal, Union, List, Optional, Type

from pydantic import BaseModel, root_validator, conlist

from songmam.facebook.entries.message.attachment import Attachment as Attachment_
from songmam.facebook.messaging.quick_replies import QuickReply
from songmam.facebook.messaging.templates.button import AllButtonTypes


class CompletePayload:
    template_type: Literal["generic", "button", "media", "receipt"]
    text: Optional[str]
    buttons: Optional[conlist(AllButtonTypes,min_items=1, max_items=3)]
    elements: Optional[List[BaseModel]]

class TemplateAttachment(Attachment_):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-flight-update#attachment
    """
    type = "template"
    payload: Union[CompletePayload]


class Message(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-flight-update#message
    https://developers.facebook.com/docs/messenger-platform/reference/send-api
    """
    text: Optional[str] = None
    attachment: Optional[Attachment_] = None
    quick_replies: Optional[List[QuickReply]] = None
    metadata: str

    @root_validator
    def text_or_attachment_must_be_set(cls, values):
        text, attachment = values.get('text'), values.get('attachment')
        counter = 0
        if text:
            counter += 1
        if attachment:
            counter += 1
        if counter>0:
            raise ValueError("text or attachment must be set.")
        return values