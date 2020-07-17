from typing import Literal, List

from pydantic import BaseModel

from songmam.facebook.messaging import Buttons


class PayloadButton(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/button
    """
    template_type: Literal["button"]
    text: str
    buttons: List[Buttons]  # Set of 1-3 buttons that appear as call-to-actions.