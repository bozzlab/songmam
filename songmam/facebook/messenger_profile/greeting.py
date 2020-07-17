# https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api/greeting
from typing import List

from pydantic import BaseModel, validator

from songmam.facebook.mess.locale import ThingWithLocale


class GreetingPerLocale(ThingWithLocale):
    text: str  # Text Could be Personalized e.g. "Hello {{user_first_name}}!"

    @validator('text')
    def char_limit_to_160(cls, value):
        if len(value) > 160:
            raise ValueError("Must be in UTF-8. 160 character limit.")


class Greeting(BaseModel):
    greeting: List[GreetingPerLocale]
