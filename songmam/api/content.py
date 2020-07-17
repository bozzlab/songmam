from dataclasses import dataclass
from typing import Optional, List


from songmam.facebook.messaging.quick_replies import QuickReply
from songmam.facebook.messaging.templates import Attachment, Message, ButtonMeesage
from songmam.facebook.messaging.templates.button import URLButton


@dataclass
class Content:
    text: str
    buttons: Optional[List[URLButton]] = None
    quick_replies: Optional[List[QuickReply]] = None

    @property
    def message(self):
        payload = ButtonMeesage(text="Sample Button")
        message = Message(attachment=Attachment(payload=payload))

        if self.buttons:
            payload.buttons = self.buttons
        if self.quick_replies:
            message.quick_replies = self.quick_replies

        return message