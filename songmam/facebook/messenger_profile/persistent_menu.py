# https://developers.facebook.com/docs/messenger-platform/send-messages/persistent-menu
from typing import List, Union

from pydantic import BaseModel


from songmam.facebook.messaging.templates.button import BaseButton, PostbackButton, URLButton
from songmam.facebook.messaging.locale import ThingWithLocale


class MenuPerLocale(ThingWithLocale):
    composer_input_disabled: bool = False
    call_to_actions: List[Union[URLButton, PostbackButton]]


class PersistentMenu(BaseModel):
    persistent_menu: List[MenuPerLocale]
    
class UserPersistentMenu(PersistentMenu):
    psid: str

