from dataclasses import dataclass
from typing import Optional, List

from songmam.facebook.messaging.payload import BasePayload
from songmam.facebook.messaging.templates import Attachment, Message
from songmam.facebook.messaging.templates.button import URLButton, Payload
from songmam.facebook.send import SendRecipient

@dataclass
class Content:
    text: str
    buttons: Optional[List[URLButton]]

    @property
    def message(self):
        return Message(attachment=Attachment(
                    payload=Payload(
                        text="Sample Button",
                        buttons=self.buttons
                    )
                ))