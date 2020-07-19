from dataclasses import dataclass
from typing import Optional, List


from songmam.facebook.messaging.quick_replies import QuickReply
from songmam.facebook.messaging.templates import TemplateAttachment, Message, CompletePayload
from songmam.facebook.messaging.templates.button import URLButton


@dataclass
class Content:
    text: str
    buttons: Optional[List[URLButton]] = None
    quick_replies: Optional[List[QuickReply]] = None

    @property
    def message(self):
        message = Message()


        if self.buttons:
            payload = CompletePayload(text=self.text)
            payload.buttons = self.buttons
            message.attachment = TemplateAttachment(payload=payload)
        else:
            message.text = self.text
        if self.quick_replies:
            message.quick_replies = self.quick_replies

        return message