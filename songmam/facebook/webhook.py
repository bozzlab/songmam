from typing import List, Union, Optional

from loguru import logger
from pydantic import BaseModel, validator

from songmam.facebook.entries.echo import EchoEntry
from songmam.facebook.entries.messages import MessageEntry, Messaging
from songmam.facebook.entries.postback import PostbackEntry, Postback


class Webhook(BaseModel):
    """An object contains one or more entries
    https://developers.facebook.com/docs/messenger-platform/reference/webhook-events/#payload
    """
    object: str
    entry: List[Union[PostbackEntry, MessageEntry, EchoEntry]]


    @validator('object')
    def object_equal_page(cls, v):
        if v != 'page':
            error_msg = "only support page subscription"
            logger.error(error_msg)
            raise ValueError(error_msg)
        return v
