from typing import Optional, Literal, List

from pydantic import BaseModel, validator

from songmam.facebook.messaging.buttonmeesage import ButtonTypeList


class MediaElements(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/media#elements
    """
    media_type: Optional[Literal["image", "video"]]
    attachment_id: Optional[str]  # Cannot be used if url is set.
    url: Optional[str]  # Cannot be used if attachment_id is set.
    buttons: Optional[List[ButtonTypeList]]  # A maximum of 1 button is supported.

    @validator('buttons')
    def buttons_limit_to_3_buttons(cls, v):
        if len(v) > 3:
            raise ValueError('Max buttons at 3 for Button Template.')
        return v


class PayloadMedia(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/media#payload
    """
    template_type: Literal["media"]
    elements: List[MediaElements]
    sharable: Optional[bool]