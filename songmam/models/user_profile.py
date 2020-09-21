from typing import Optional, Any

from pydantic import BaseModel, HttpUrl


class UserProfile(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/identity/user-profile
    """

    id: str
    name: str
    first_name: str
    last_name: str
    profile_pic: HttpUrl
    locale: Optional[str]  # TODO: to be changed to `literal`
    timezone: Optional[int]
    gender: Optional[str]  # TODO: to be changed to `literal`
