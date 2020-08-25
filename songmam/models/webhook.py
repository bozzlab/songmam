from typing import List, Union, Optional

from loguru import logger
from pydantic import BaseModel, validator

from songmam.models.entries.deliveries import DeliveriesEntry
from songmam.models.entries.echo import EchoEntry
from songmam.models.entries.messages import MessageEntry
from songmam.models.entries.postback import PostbackEntry


class Webhook(BaseModel):
    """An object contains one or more entries
    https://developers.facebook.com/docs/messenger-platform/reference/webhook-events/#payload
    """
    object: str
    entry: List[Union[DeliveriesEntry, PostbackEntry, MessageEntry, EchoEntry]]

    @validator('object')
    def object_equal_page(cls, v):
        if v != 'page':
            error_msg = "only support page subscription"
            logger.error(error_msg)
            raise ValueError(error_msg)
        return v
