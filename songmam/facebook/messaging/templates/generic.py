from typing import Optional, List, Literal, Type

from pydantic import BaseModel, HttpUrl

from songmam.facebook.messaging.templates import CompletePayload
from songmam.facebook.messaging.templates.button import BaseButton




class GenericElements(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/generic#elements
    """
    title: str
    subtitle: Optional[str]
    image_url: Optional[HttpUrl]
    default_action: Optional[Type[BaseButton]]
    buttons: Optional[Type[BaseButton]]


class PayloadGeneric(CompletePayload):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/generic
    """
    template_type = "generic"
    image_aspect_ratio: Optional[Literal["horizontal", "square"]] = None
    elements: List[GenericElements]


