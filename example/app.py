from typing import Any, Dict

from fastapi import FastAPI, Request

# from songmam import Page, Webhook, MessageEvent, BasePayload

# os.environ['PAGE_ACCESS_TOKEN'] = "MY Access token"
# os.environ['PAGE_VERIFY_TOKEN'] = "MY Verify token"
from songmam import Webhook
from songmam.api.events import MessageEvent
from songmam.api.content import Content
from songmam.facebook.messaging.locale import Locale
from songmam.facebook.messaging.templates.button import URLButton, PostbackButton, CallButton
from songmam.facebook.messenger_profile import MenuPerLocale
from songmam.page import Page


default_menu = MenuPerLocale(
    call_to_actions=[
        PostbackButton(title='menu 1', payload='menu 1'),
        PostbackButton(title='menu 2', payload='menu 2')
    ]
)
th_menu = MenuPerLocale(
    locale=Locale.th_TH,
    call_to_actions=[
        PostbackButton(title='เมนู 1', payload='เมนู 1'),
        PostbackButton(title='เมนู 2', payload='เมนู 2')
    ]
)

page = Page(persistent_menu=[default_menu, th_menu])
app = FastAPI()

page.add_verification_middleware(app)
page.auto_mark_as_seen = False

# page.set_user_menu()

@app.get("/healthz")
async def show_server_is_alive(request: Request):
    body = await request.body()
    return "server is online."

# @app.post("/webhook")
# async def handle_entry(webhook: Webhook, request: Request):
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

    page.get_user_profile(message.sender.id)
    # page.send(message.sender.id, "thank you! your message is '%s'" % message.text)
    buttons = [
        URLButton(title="Open Web URL", url="https://www.oculus.com/en-us/rift/"),
        PostbackButton(title="trigger Postback", payload="DEVELOPED_DEFINED_PAYLOAD"),
        CallButton(title="Call Phone Number", payload="+66992866936")
    ]

    # you can use a dict instead of a Button class
    #
    # buttons = [{'type': 'web_url', 'title': 'Open Web URL', 'value': 'https://www.oculus.com/en-us/rift/'},
    #          {'type': 'postback', 'title': 'trigger Postback', 'value': 'DEVELOPED_DEFINED_PAYLOAD'},
    #          {'type': 'phone_number', 'title': 'Call Phone Number', 'value': '+16505551234'}]

    content = Content(
        text="Sample Button",
        buttons=buttons
    )
    page.send(message.sender, content)
    # page.reply(message, content)
    # page._send(
    #
    #     )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True, log_level='debug')