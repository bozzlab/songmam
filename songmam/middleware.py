from typing import Optional

from starlette.responses import PlainTextResponse, Response
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.requests import Request


class VerificationMiddleware:
    """Verify middleware that follows the step 4: Add webhook verification
    https://developers.facebook.com/docs/messenger-platform/getting-started/webhook-setup
    """
    def __init__(self, app: ASGIApp, verify_token: str, route_webhook: Optional[str] = None) -> None:
        self.app = app
        self.verify_token = verify_token
        self.route_webhook = route_webhook

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            request = Request(scope, receive)

            if request.method == 'GET':
                query_params = request.query_params
                criteria = {'hub.mode', 'hub.verify_token', 'hub.challenge'}
                if set(query_params.keys()).issuperset(criteria):
                    mode = query_params.get('hub.mode')
                    test_token = query_params.get('hub.verify_token')
                    challenge = query_params.get('hub.challenge')
                    if mode and test_token:
                        if mode == 'subscribe' and test_token == self.verify_token:
                            response = PlainTextResponse(challenge)
                        else:
                            response = Response("", status_code=403)

                        await response(scope, receive, send)
                        return
            await self.app(scope, receive, send)
