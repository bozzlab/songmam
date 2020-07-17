from typing import Literal, Optional

from pydantic import BaseModel, validator, HttpUrl, root_validator


class DefaultAction(BaseModel):
    """ # Mentioned as URL Button with no 'title'
    https://developers.facebook.com/docs/messenger-platform/reference/buttons/url
    """
    type: str = "web_url"
    url: HttpUrl
    webview_height_ratio: Literal["compact", "tall", "full"] = 'full'
    messenger_extensions: bool = False
    fallback_url: HttpUrl
    webview_share_button: Optional[str]


class BaseButton(BaseModel):
    type: str
    title: str

    @validator('title')
    def title_limit_to_20_characters(cls, v):
        if len(v) > 20:
            raise ValueError('Button title. 20 character limit.')
        return v


class URLButton(BaseButton):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/buttons/url
    Updated: 04/07/2020
    """
    type: str = 'web_url'
    title: str
    url: HttpUrl
    webview_height_ratio: Literal['compact', 'tall', 'full'] = 'full'
    messenger_extensions: bool = False
    fallback_url: Optional[HttpUrl]
    webview_share_button: Optional[Literal['hide']]


    @root_validator
    def fallback_url_should_not_be_specify_if_messenger_extensions_is_false(cls, values):
        messenger_extensions, fallback_url = values.get('messenger_extensions'),values.get('fallback_url')
        if fallback_url:
            if not messenger_extensions:
                raise ValueError('`fallback_url` may only be specified if `messenger_extensions` is true.')
        return values


class PostBackButton(BaseButton):
    type: str = 'postback'
    payload: str


class CallButton(BaseButton):
    type: str = 'phone_number'
    payload: str

    # TODO: https://pypi.org/project/phonenumbers/


class LogInButton(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/send-messages/buttons#login
    """
    type: str = "account_link"
    url: HttpUrl  # Authentication callback URL. Must use HTTPS protocol.


class LogOutButton(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/buttons/logout
    """
    type: str = "account_unlink"


class GameMetadata(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/buttons/game-play#game_metadata
    """
    player_id: Optional[str]
    context_id: Optional[str]


class GamePlayButton(BaseButton):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/buttons/game-play
    """
    type: str = "game_play"
    title: str
    payload: Optional[str]
    game_metadata: Optional[GameMetadata]


class Buttons(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/buttons/url#properties
    """
    type: Literal["web_url", "postback", "phone_number", "account_link", "account_unlink", "game_play"]
    title: str
    payload: Optional[str]  # for type : postback / phone_number / game_play
    url: Optional[HttpUrl]  # for type: web_url / LogIn
    webview_height_ratio: Optional[Literal["compact", "tall", "full"]]  # for type: web_url
    messenger_extensions: Optional[bool]  # for type: web_url
    fallback_url: Optional[HttpUrl]  # for type: web_url
    webview_share_button: Optional[str]  # for type: web_url
    game_metadata: Optional[GameMetadata]  # for type : game_play