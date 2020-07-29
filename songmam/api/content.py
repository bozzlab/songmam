from dataclasses import dataclass
from typing import Optional, List

from songmam.facebook.messaging.quick_replies import QuickReply
from songmam.facebook.messaging.templates import TemplateAttachment, Message
from songmam.facebook.messaging.templates.receipt import ReceiptElements, Address, Summary, Adjustments, PayloadReceipt


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
