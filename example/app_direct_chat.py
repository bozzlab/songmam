import os
from typing import Any, Dict

from decouple import config
from fastapi import FastAPI, Body, Request
from loguru import logger

from songmam import Page, VerificationMiddleware, Webhook, MessageEvent, ButtonWeb, ButtonPostBack, ButtonPhoneNumber, \
    Buttons

# os.environ['PAGE_ACCESS_TOKEN'] = "MY Access token"
# os.environ['PAGE_VERIFY_TOKEN'] = "MY Verify token"

page = Page()
app = FastAPI()

page.add_verification_middleware(app)

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
async def echo(message: MessageEvent):
    # page.get_user_profile(message.recipient.id)
    # page.send(message.recipient.id, "thank you! your message is '%s'" % message.text)
    # buttons = [
    #     ButtonWeb(title="Open Web URL", url="https://www.oculus.com/en-us/rift/"),
    #     ButtonPostBack(title="trigger Postback", payload="DEVELOPED_DEFINED_PAYLOAD"),
    #     ButtonPhoneNumber(title="Call Phone Number", payload="+16505551234")
    # ]
    logger.info(f"{message.sender.id} sent {message.text}")

    ben_id = "2892682217518683"
    pat_id = "3035678546494620"

    if message.sender.id == ben_id:
        page.send_sync(pat_id, message.text)
    elif message.sender.id == pat_id:
        page.send_sync(ben_id, message.text)
    else:
        page.send_sync(message.sender.id, "thank you! your message is '%s'" % message.text)


    # you can use a dict instead of a Button class
    #
    # buttons = [{'type': 'web_url', 'title': 'Open Web URL', 'value': 'https://www.oculus.com/en-us/rift/'},
    #          {'type': 'postback', 'title': 'trigger Postback', 'value': 'DEVELOPED_DEFINED_PAYLOAD'},
    #          {'type': 'phone_number', 'title': 'Call Phone Number', 'value': '+16505551234'}]

    # page.send(message.recipient.id, Buttons("hello", buttons))

if __name__ == "__main__":

    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True, log_level='debug')