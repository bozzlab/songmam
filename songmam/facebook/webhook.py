from typing import List, Union, Optional

from loguru import logger
from pydantic import BaseModel, validator

from songmam.facebook.entries.messages import MessageEntry, Messaging
from songmam.facebook.entries.postbacks import PostbacksEntry, Postbacks


class GenericEntry(BaseModel):
    id: Optional[str]
    time: Optional[int]
    messaging: Optional[List[Messaging]]
    postback: Optional[Postbacks]

    def convert_to_specific(self):
        if self.messaging:
            return MessageEntry(**self.dict())
        elif self.postback:
            return PostbacksEntry(**self.dict())

class Webhook(BaseModel):
    """An object contains one or more entries
    https://developers.facebook.com/docs/messenger-platform/reference/webhook-events/#payload
    """
    object: str
    entry: List[Union[MessageEntry, PostbacksEntry]]

    # @validator('entry')
    # def get_the_right_type(cls, value):
    #     if getattr(value, 'messaging'):
    #         return

    @validator('object')
    def object_equal_page(cls, v):
        if v != 'page':
            error_msg = "only support page subscription"
            logger.error(error_msg)
            raise ValueError(error_msg)
        return v
