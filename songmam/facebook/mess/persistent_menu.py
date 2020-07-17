# https://developers.facebook.com/docs/messenger-platform/send-messages/persistent-menu
from enum import auto
from typing import List

from pydantic import BaseModel


from songmam.facebook.mess.buttons import BaseButton
from songmam.facebook.mess.locale import ThingWithLocale




class MenuPerLocale(ThingWithLocale):
    composer_input_disabled: bool = False
    call_to_actions: List[BaseButton]


class PersistentMenu(BaseModel):
    persistent_menu: List[MenuPerLocale]
    
class UserPersistentMenu(PersistentMenu):
    psid: str

