from typing import Any, Dict

from fastapi import FastAPI, Body, Request

from songmam import Page, VerificationMiddleware, Webhook, TextMessage, MessageEvent
from songmam.webhook import Entry

page = Page("EAAo8TBakcvcBAORRcGRraHxdhFO3mLEZB5Yy9wnFbXsZAuT17xZCdgkQWN36u7cJ0vr8UHfKvTvVIZCEzbK4FFDWywcZA4CQ0G9JcKZB5UPrmm0SYzmOtOZAxeiDTplKwcqMpJoH8JuFWVekMc0orhjhFiinNgrsR0ZBlOMZBEYVxTGuVitlXvR7AfmvqWvsHHpcZD", "abc")

app = FastAPI()

app.add_middleware(VerificationMiddleware, verify_token=page.verify_token)



@app.get("/healthz")
async def show_server_is_alive(request: Request):
    body = await request.body()
    return "server is online."

# @app.post("/webhook")
# async def handle_entry(webhook: Webhook, request: Request):
#     # body = await request.body()
#     # # webhook = Webhook.parse_raw(body)
#     # print(body)
#     # print(webhook)
#     await page.handle_webhook(webhook)
#     return "ok"

@app.post("/webhook")
async def handle_entry(webhook: Dict[str, Any], request: Request):
    body = await request.body()
    webhook = Webhook.parse_raw(body)
    # print(body)
    print(webhook)
    await page.handle_webhook(webhook)
    return "ok"

@page.handle_message
def echo(message: MessageEvent):
    page.send(message.sender.id, "thank you! your message is '%s'" % message.text)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True, log_level='debug')