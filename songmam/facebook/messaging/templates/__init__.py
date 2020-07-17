from typing import Literal, Union, List

from pydantic import BaseModel

from songmam.facebook.messaging.templates.button import Payload


class Attachment(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-flight-update#attachment
    """
    type: Literal["template"] = "template"
    payload: Union[Payload]


class Message(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-flight-update#message
    """
    attachment: Attachment