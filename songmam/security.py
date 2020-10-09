import base64
import hashlib
import hmac
import json
from typing import Dict
from typing import NewType
from typing import Optional

import arrow


def base64_url_decode(inp) -> bytes:
    padding_factor = (4 - len(inp) % 4) % 4
    inp += "=" * padding_factor
    return base64.b64decode(inp.translate(dict(zip(map(ord, "-_"), "+/"))))


RequestContent = Dict


def verify_signed_request(signed_request, app_secret) -> Optional[RequestContent]:
    """
    Verify Signed Request from Context object retrieves from webview, frontend
    https://developers.facebook.com/docs/messenger-platform/webview/context

    fork from https://gist.github.com/adrienjoly/1373945/0434b4207a268bdd9cbd7d45ac22ec33dfaad199
    """
    encoded_signature, payload = signed_request.split(".")

    signature = base64_url_decode(encoded_signature)
    request_content = json.loads(base64_url_decode(payload))

    if request_content.get("algorithm").upper() != "HMAC-SHA256":
        raise NotImplementedError("Unknown algorithm")
    else:
        calculated_signature = hmac.new(
            str.encode(app_secret), str.encode(payload), hashlib.sha256
        ).digest()

    if signature != calculated_signature:
        return None
    else:
        return request_content


def verify_webhook_body(signature, app_secret, body):
    """
    https://developers.facebook.com/docs/messenger-platform/webhook#security
    """
    # signature = request.headers["X-Hub-Signature"]
    assert len(signature) == 45
    assert signature.startswith("sha1=")
    signature = signature[5:]

    # body = await request.body()
    expected_signature = hmac.new(
        str.encode(app_secret), body, hashlib.sha1
    ).hexdigest()

    if expected_signature != signature:
        return False

    return True
