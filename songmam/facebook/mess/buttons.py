from typing import Literal, Optional

from pydantic import BaseModel, validator, HttpUrl, root_validator


class BaseButton(BaseModel):
    type: str
    title: str

    @validator('title')
    def title_limit_to_20_characters(cls, v):
        if len(v) > 20:
            raise ValueError('Button title. 20 character limit.')
        return v

class ButtonWeb(BaseButton):
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


class ButtonPostBack(BaseButton):
    type: str = 'postback'
    payload: str

class ButtonPhoneNumber(BaseButton):
    type = 'phone_number'
    payload: str

    # TODO: https://pypi.org/project/phonenumbers/