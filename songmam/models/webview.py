import base64
import hashlib
import hmac
from enum import auto
from typing import NewType
from typing import Optional

import arrow
from autoname import AutoNameUppercase
from pydantic import BaseModel
from pydantic.types import conint

from songmam.security import verify_signed_request

# type
Second = conint(ge=0)


class ThreadType(AutoNameUppercase):
    user_to_page = auto()
    user_to_user = auto()
    group = auto()


class SignedRequestContent(BaseModel):
    """
    This class property was created based on a real object. See test for ref.

    # WTF, This is not the same structure as the actual object
    https://developers.facebook.com/docs/reference/login/signed-request
    """

    # code: Optinal[str]
    algorithm: str
    issued_at: int
    # user_id: str
    page_id: str
    psid: str
    thread_type: ThreadType
    tid: str
    # oauth_token
    # expires
    # app_data


class Context(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/messenger-extensions-sdk/getContext
    """

    thread_type: ThreadType
    tid: str
    psid: str
    signed_request: str

    def verify(
        self, app_secret, acceptable_freshness: Optional[Second] = None
    ) -> Optional[SignedRequestContent]:
        """
        verify signed_request alongwith fressness
        https://developers.facebook.com/docs/messenger-platform/webview/context

        fork from https://gist.github.com/adrienjoly/1373945/0434b4207a268bdd9cbd7d45ac22ec33dfaad199
        """

        request_content = verify_signed_request(
            app_secret=app_secret, signed_request=self.signed_request
        )
        if request_content:
            request_content = SignedRequestContent(**request_content)
        else:
            return None

        if acceptable_freshness:
            issued_at = arrow.get(request_content.issued_at)
            if issued_at.shift(seconds=acceptable_freshness) < arrow.utcnow():
                raise Exception(
                    f"This context is too old. It was issue at {issued_at.format()}"
                )

        return request_content
