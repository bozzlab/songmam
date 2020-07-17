from enum import auto
from typing import Optional, List, Any

from pydantic import BaseModel, HttpUrl

from songmam.facebook.messenger_profile.greeting import GreetingPerLocale
from songmam.facebook.messenger_profile.persistent_menu import MenuPerLocale
from songmam.utils import AutoName


class MessengerProfileProperty(AutoName):
    get_started = auto()
    greeting = auto()
    ice_breakers = auto()
    persistent_menu = auto()
    whitelisted_domains = auto()
    account_linking_url = auto()

class MessengerProfile(BaseModel):
    get_started: Any
    greeting: Optional[List[GreetingPerLocale]]
    ice_breakers: Any
    persistent_menu: Optional[List[MenuPerLocale]]
    whitelisted_domains: Any
    account_linking_url: Optional[HttpUrl]

