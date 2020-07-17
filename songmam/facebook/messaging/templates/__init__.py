from typing import Literal, Union, List, Type

from pydantic import BaseModel, validator

from songmam.facebook.messaging import BaseButton
from songmam.facebook.messaging.quick_replies import QuickReply


class ButtonMeesage(Message):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/button
    """
    template_type = 'button'
    text: str
    buttons: List[Type[BaseButton]] = None # Set of 1-3 buttons that appear as call-to-actions.

    @validator('text')
    def title_limit_to_640_characters(cls, v):
        if len(v) > 640:
            raise ValueError('UTF-8-encoded text of up to 640 characters.')
        return v

    @validator('buttons')
    def limit_buttons_from_1_to_3(cls, value):
        num_char = len(value)
        if num_char < 0 or num_char > 3:
            raise ValueError('Set of 1-3 buttons only.')
        return value

class Attachment(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-flight-update#attachment
    """
    type: Literal["template"] = "template"
    payload: Union[ButtonMeesage]


class Message(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-flight-update#message
    """
    attachment: Attachment
    quick_replies: List[QuickReply] = None


