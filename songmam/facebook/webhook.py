from typing import List, Union

from loguru import logger
from pydantic import BaseModel, validator

from songmam.facebook.entries.messages import MessageEntry
from songmam.facebook.entries.postbacks import PostbacksEntry


class Webhook(BaseModel):
    """An object contains one or more entries
    https://developers.facebook.com/docs/messenger-platform/reference/webhook-events/#payload
    """
    object: str
    entry: List[Union[MessageEntry, PostbacksEntry]]

    @validator('object')
    def object_equal_page(cls, v):
        if v != 'page':
            error_msg = "only support page subscription"
            logger.error(error_msg)
            raise ValueError(error_msg)
        return v
