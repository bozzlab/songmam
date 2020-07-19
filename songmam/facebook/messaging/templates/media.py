from typing import Optional, Literal, List

from pydantic import BaseModel, validator, conlist

from songmam.facebook.messaging.templates.button import AllButtonTypes


class MediaElements(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/media#elements
    """
    media_type: Optional[Literal["image", "video"]]
    attachment_id: Optional[str]  # Cannot be used if url is set.
    url: Optional[str]  # Cannot be used if attachment_id is set.
    buttons: Optional[conlist(AllButtonTypes, min_items=1, max_items=3)]  # A maximum of 1 button is supported.


class PayloadMedia(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/media#payload
    """
    template_type: Literal["media"]
    elements: conlist(MediaElements, max_items=1)
    sharable: Optional[bool]