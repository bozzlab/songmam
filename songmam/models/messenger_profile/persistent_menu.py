# https://developers.facebook.com/docs/messenger-platform/send-messages/persistent-menu
from typing import List, Union

from pydantic import BaseModel, conlist

from songmam.models.messaging.templates.button import (
    BaseButton,
    PostbackButton,
    URLButton,
)
from songmam.models.messaging.locale import ThingWithLocale


class MenuPerLocale(ThingWithLocale):
    composer_input_disabled: bool = False
    call_to_actions: conlist(Union[URLButton, PostbackButton], min_items=1)


class PersistentMenu(BaseModel):
    persistent_menu: List[MenuPerLocale]


class UserPersistentMenu(PersistentMenu):
    psid: str
