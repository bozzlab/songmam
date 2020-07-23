from dataclasses import dataclass
from typing import Optional, List, Literal

from pydantic import conlist, HttpUrl

from songmam.facebook.messaging.quick_replies import QuickReply
from songmam.facebook.messaging.templates import TemplateAttachment, Message
from songmam.facebook.messaging.templates.button import AllButtonTypes, PayloadButtonTemplate
from songmam.facebook.messaging.templates.generic import GenericElements, PayloadGeneric
from songmam.facebook.messaging.templates.media import MediaElements, PayloadMedia
from songmam.facebook.messaging.templates.receipt import ReceiptElements, Address, Summary, Adjustments, PayloadReceipt


@dataclass
class ContentButton:
    text: str
    buttons: Optional[conlist(AllButtonTypes, min_items=1, max_items=3)]
    quick_replies: Optional[List[QuickReply]]

    @property
    def message(self):
        message = Message()

        if self.buttons:
            payload = PayloadButtonTemplate(
                template_type='button',
                text=self.text,
                buttons=self.buttons
            )
            message.attachment = TemplateAttachment(
                payload=payload
            )
        else:
            message.text = self.text
        if self.quick_replies:
            message.quick_replies = self.quick_replies

        return message


@dataclass
class ContentGeneric:
    quick_replies: Optional[List[QuickReply]]
    elements: List[GenericElements]
    image_aspect_ratio: Optional[Literal["horizontal", "square"]]

    @property
    def message(self):
        message = Message()

        if self.elements:
            payload = PayloadGeneric(
                template_type="generic",
                elements=self.elements
            )
            payload.image_aspect_ratio = self.image_aspect_ratio
            message.attachment = TemplateAttachment(
                payload=payload
            )
        if self.quick_replies:
            message.quick_replies = self.quick_replies

        return message


@dataclass
class ContentMedia:
    quick_replies: Optional[List[QuickReply]]
    elements: List[MediaElements]
    sharable: Optional[bool]

    @property
    def message(self):
        message = Message()

        if self.elements:
            payload = PayloadMedia(
                template_type="media",
                elements=self.elements,
                sharable=self.sharable
            )
            message.attachment = TemplateAttachment(
                payload=payload
            )
        if self.quick_replies:
            message.quick_replies = self.quick_replies

        return message


@dataclass
class ContentReceipt:
    quick_replies: Optional[List[QuickReply]]
    sharable: Optional[bool]
    recipient_name: str
    merchant_name: Optional[str]
    order_number: str
    currency: str
    payment_method: str  # This can be a custom string, such as, "Visa 1234".
    timestamp: Optional[str]
    elements: Optional[List[ReceiptElements]]
    address: Optional[Address]
    summary: Summary
    adjustments: Optional[List[Adjustments]]

    @property
    def message(self):
        message = Message()

        if self.elements:
            payload = PayloadReceipt(
                template_type="receipt",
                recipient_name=self.recipient_name,
                order_number=self.order_number,
                currency=self.currency,
                payment_method=self.payment_method,  # This can be a custom string, such as, "Visa 1234".
                summary=self.summary,
            )
            payload.sharable = self.sharable
            payload.merchant_name = self.merchant_name
            payload.timestamp = self.timestamp
            payload.elements = self.elements
            payload.address = self.address
            payload.adjustments = self.adjustments
            message.attachment = TemplateAttachment(
                payload=payload
            )
        if self.quick_replies:
            message.quick_replies = self.quick_replies

        return message
