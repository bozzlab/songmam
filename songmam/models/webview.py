import base64
import hashlib
import hmac
import json
from enum import auto

from autoname import AutoNameUppercase
from pydantic import BaseModel


class ThreadType(AutoNameUppercase):
    user_to_page = auto()
    user_to_user = auto()
    group = auto()

class UnsignedRequest(BaseModel):
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

    @staticmethod
    def base64_url_decode(inp):
        padding_factor = (4 - len(inp) % 4) % 4
        inp += "=" * padding_factor
        return base64.b64decode(inp.translate(dict(zip(map(ord, u'-_'), u'+/'))))

    def verify(self, app_secret) -> UnsignedRequest:
        """
        https://developers.facebook.com/docs/messenger-platform/webview/context

        fork from https://gist.github.com/adrienjoly/1373945/0434b4207a268bdd9cbd7d45ac22ec33dfaad199
        """
        encoded_signature, payload = self.signed_request.split('.')

        signature = self.base64_url_decode(encoded_signature)
        unsigned_request = UnsignedRequest.parse_raw(self.base64_url_decode(payload))

        if unsigned_request.algorithm.upper() != 'HMAC-SHA256':
            raise NotImplementedError('Unknown algorithm')
        else:
            expected_signature = hmac.new(
                str.encode(app_secret), str.encode(payload), hashlib.sha256
            ).hexdigest()

        if signature != expected_signature:
            return None
        else:
            return unsigned_request


