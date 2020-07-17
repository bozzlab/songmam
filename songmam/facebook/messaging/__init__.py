# https://developers.facebook.com/docs/messenger-platform/send-messages#send_api_basics
from typing import Literal, List, Optional
from enum import auto

from pydantic import BaseModel, HttpUrl


from enum import auto

from songmam.utils import AutoName


class ButtonType(AutoName):
    web_url = auto()
    postback = auto()
    phone_number = auto()
    account_link = auto()
    account_unlink = auto()
    game_play = auto()


class DefaultAction(BaseModel):
    """ # Mentioned as URL Button with no 'title'
    https://developers.facebook.com/docs/messenger-platform/reference/buttons/url
    """
    type: Literal["web_url"]
    url: HttpUrl
    webview_height_ratio: Optional[Literal["compact", "tall", "full"]]
    messenger_extensions: Optional[bool]
    fallback_url: HttpUrl
    webview_share_button: Optional[str]




from songmam.utils import AutoNameLower


class SenderAction(AutoNameLower):
    """https://developers.facebook.com/docs/messenger-platform/send-messages/sender-actions"""
    TYPING_ON = auto()
    TYPING_OFF = auto()
    MARK_SEEN = auto()
