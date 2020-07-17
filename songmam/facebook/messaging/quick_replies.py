#  QUICK REPLIES START
from typing import Literal, Optional, Union, List

from pydantic import BaseModel, HttpUrl

from songmam.facebook import ThingWithID


class QuickReplies(BaseModel):
    content_type: Literal["text", "location", "user_phone_number", "user_email"]
    title: Optional[str]  # Required if content_type is 'text'
    payload: Optional[Union[str, int]]  # "payload":"<POSTBACK_PAYLOAD>"
    image_url: Optional[HttpUrl]  # Required if title is an empty string.


class SendingQuickRepliesMessage(BaseModel):
    text: str
    quick_replies: List[QuickReplies]





#  END OF QUICK REPLIES

###############################################################
