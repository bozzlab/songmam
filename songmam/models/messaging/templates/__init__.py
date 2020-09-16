from typing import Literal, Union, List, Optional

from pydantic import BaseModel

from songmam.models.webhook.events.message.attachment import Attachment as Attachment_
from songmam.models.messaging.quick_replies import QuickReply
from songmam.models.messaging.templates.button import (
    AllButtonTypes,
    PayloadButtonTemplate,
)
from songmam.models.messaging.templates.generic import PayloadGeneric
from songmam.models.messaging.templates.media import PayloadMedia
from songmam.models.messaging.templates.receipt import (
    ReceiptElements,
    Address,
    Summary,
    Adjustments,
    PayloadReceipt,
)
from songmam.models.messaging.templates.button import AllButtonTypes


class TemplateAttachment(Attachment_):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-flight-update#attachment
    """

    type: Literal[
        "audio", "file", "image", "location", "video", "fallback", "template"
    ] = "template"
    payload: Union[PayloadReceipt, PayloadGeneric, PayloadMedia, PayloadButtonTemplate]


class Message(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-flight-update#message
    https://developers.facebook.com/docs/messenger-platform/reference/send-api
    """

    text: Optional[str]
    attachment: Optional[TemplateAttachment]
    quick_replies: Optional[List[QuickReply]]
    metadata: Optional[str]

    # TODO: Fix this validator
    # @root_validator
    # def text_or_attachment_must_be_set(cls, values):
    #     text, attachment = values.get('text'), values.get('attachment')
    #     counter = 0
    #     if text:
    #         counter += 1
    #     if attachment:
    #         counter += 1
    # TODO: Fix this validator : This line will caused the incomplete initialiazation to throw error. m=Message(), m.text="cat"
    #     if counter == 0:
    #         raise ValueError("text or attachment must be set.")
    #     return values
