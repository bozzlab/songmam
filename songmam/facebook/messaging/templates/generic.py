from typing import Optional, List, Literal

from pydantic import BaseModel, HttpUrl

from songmam.facebook.messaging import DefaultAction
from songmam.facebook.messaging.buttonmeesage import ButtonTypeList


class GenericElements(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/generic#elements
    """
    title: str
    subtitle: Optional[str]
    image_url: Optional[HttpUrl]
    default_action: Optional[DefaultAction]
    buttons: Optional[List[ButtonTypeList]]


class PayloadGeneric(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/generic
    """
    template_type: Literal["generic"]
    image_aspect_ratio: Optional[Literal["horizontal", "square"]]
    elements: List[GenericElements]