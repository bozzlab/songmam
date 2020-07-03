from typing import Union, List

from loguru import logger
from pydantic import BaseModel, validator

from songmam.events.base import Messaging
from songmam.events.messages import TextMessage


class Entry(BaseModel):
    id: str
    time: int
    messaging: List[TextMessage]

    @property
    def theMessaging(self):
        return self.messaging[0]

    @validator('messaging')
    def messaging_must_has_one_and_only_one_element(cls, v):
        assert len(v) == 1
        return v

class Webhook(BaseModel):
    """An object contains one or more events
    https://developers.facebook.com/docs/messenger-platform/reference/webhook-events/#payload
    """
    object: str
    entry: List[Entry]

    @validator('object')
    def object_equal_page(cls, v):
        if v != 'page':
            error_msg= "only support page subscription"
            logger.error(error_msg)
            raise ValueError(error_msg)
        return v
