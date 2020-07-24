from typing import Optional, List, Literal

from pydantic import BaseModel, HttpUrl, conlist

from songmam.facebook.messaging.templates.button import AllButtonTypes


class DefaultAction(BaseModel):
    """
    In reference said as a URLButton with no title
    https://developers.facebook.com/docs/messenger-platform/reference/buttons/url
    """
    type: str = 'web_url'
    url: HttpUrl
    webview_height_ratio: Literal['compact', 'tall', 'full'] = 'full'
    messenger_extensions: bool = False
    fallback_url: Optional[HttpUrl]
    webview_share_button: Optional[Literal['hide']]


class GenericElements(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/generic#elements
    """
    title: str
    subtitle: Optional[str]
    image_url: Optional[HttpUrl]
    default_action: Optional[DefaultAction]  # link to url if press on the image that showed
    buttons: Optional[conlist(AllButtonTypes, min_items=1, max_items=3)]


class PayloadGeneric(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/generic
    """
    template_type: str = "generic"
    image_aspect_ratio: Optional[Literal["horizontal", "square"]]
    elements: List[GenericElements]
