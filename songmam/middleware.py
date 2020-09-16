import hashlib
import hmac
from typing import Optional

from starlette.responses import PlainTextResponse, Response
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.requests import Request


class BaseMiddleware:
    pass


class VerifyTokenMiddleware:
    """Verify middleware that follows the step 4: Add webhook verification
    https://developers.facebook.com/docs/messenger-platform/getting-started/webhook-setup
    """

    def __init__(
        self, app: ASGIApp, path: str, verify_token: Optional[str] = None
    ) -> None:
        self.app = app
        self.verify_token = verify_token
        self.path = path

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            request = Request(scope, receive)

            query_params = request.query_params
            mode = query_params.get("hub.mode")
            test_token = query_params.get("hub.verify_token")
            challenge = query_params.get("hub.challenge")

            if request.url.path == self.path and request.method == "GET":
                if not self.verify_token:
                    response = PlainTextResponse(challenge)
                    await response(scope, receive, send)
                    return
                criteria = {"hub.mode", "hub.verify_token", "hub.challenge"}
                if set(query_params.keys()).issuperset(criteria):

                    if mode and test_token:
                        if mode == "subscribe" and test_token == self.verify_token:
                            response = PlainTextResponse(challenge)
                        else:
                            response = Response("", status_code=403)

                        await response(scope, receive, send)
                        return
            await self.app(scope, receive, send)


class AppSecretMiddleware:
    """WebhookEventValidate
    https://developers.facebook.com/docs/messenger-platform/webhook#security
    """

    def __init__(
        self, app: ASGIApp, app_secret: str, path: Optional[str] = None
    ) -> None:
        self.app = app
        self.app_secret = app_secret
        self.path = path

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            request = Request(scope, receive)

            if request.method == "POST" and request.url.path == self.path:
                header_signature = request.headers["X-Hub-Signature"]
                if len(header_signature) == 45 and header_signature.startswith("sha1="):
                    header_signature = header_signature[5:]
                else:
                    raise NotImplementedError("Dev: how to handle this?")

                body = await request.body()
                expected_signature = hmac.new(
                    str.encode(self.app_secret), body, hashlib.sha1
                ).hexdigest()

                if expected_signature != header_signature:
                    raise AssertionError("SIGNATURE VERIFICATION FAIL")

            await self.app(scope, receive, send)
