import os
from functools import partial
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# from songmam import Page, Webhook, MessageEvent, BasePayload
from songmam.api import content
from songmam.facebook.entries.messages import Sender
from songmam.facebook.messaging.templates import ReceiptElements, Address, Summary, Adjustments
from songmam.facebook.messaging.templates.generic import GenericElements, DefaultAction
from songmam.facebook.messaging.templates.media import MediaElements

# os.environ['PAGE_ACCESS_TOKEN'] = "MY Access token"
# os.environ['PAGE_VERIFY_TOKEN'] = "MY Verify token"
from furl import furl
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
from loguru import logger

from songmam import Webhook
from songmam.api.events import MessageEvent, PostBackEvent, EchoEvent, DeliveriesEvent
from songmam.api.content import ContentButton, ContentGeneric, ContentMedia, ContentReceipt
from songmam.facebook.messaging.locale import Locale
from songmam.facebook.messaging.quick_replies import QuickReply
from songmam.facebook.messaging.templates.button import URLButton, PostbackButton, CallButton, LogInButton, \
    LogOutButton, GamePlayButton
from songmam.facebook.messenger_profile import MenuPerLocale, GreetingPerLocale
from songmam.humanTyping import HumanTyping
from songmam.page import Page

endpoint_url = furl("https://170f43db701d.ngrok.io/")

# default_menu = MenuPerLocale(
#     call_to_actions=[
#         PostbackButton(title='change who i talk to', payload='menu/1'),
#         PostbackButton(title='change my menu', payload='menu/2'),
#         URLButton(title='send example replies', url=(endpoint_url / "sampleMessagerSDK").url)
#     ]
# )
# th_menu = MenuPerLocale(
#     locale=Locale.th_TH,
#     call_to_actions=[
#         PostbackButton(title='เมนู 1', payload='menu/1'),
#         PostbackButton(title='เมนู 2', payload='menu/1')
#     ]
# )
#
# default_greeting = GreetingPerLocale(text="Hi {{user_first_name}}, This is Songmum Bot." )
# th_greeting = GreetingPerLocale(locale=Locale.th_TH, text="สวัสดีครัช {{user_first_name}}, เรียกผมว่า ส่งแหม่!" )


page = Page(
    # persistent_menu=[default_menu, th_menu],
    # greeting=[default_greeting, th_greeting],
    persistent_menu=None,
    greeting=None,
    whitelisted_domains=[endpoint_url.url],
    auto_mark_as_seen=True,
)
app = FastAPI(
    title="Showcase Project",
    description="This is a very fancy project.",
    version="3.0.0",
)
humanTyping = HumanTyping()


env = Environment(
    loader=FileSystemLoader(Path()/ 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

page.add_verification_middleware(app)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/healthz")
async def show_server_is_alive(request: Request):
    body = await request.body()
    return "server is online."

# @app.post("/webhook")
# async def handle_entry(webhook: Webhook):
#     await page.handle_webhook(webhook)
#     return "ok"

@app.get("/sampleMessagerSDK", response_class=HTMLResponse)
async def sample():
    template = env.get_template('allResponse.html')
    return template.render()

@app.get("/sampleMessagerSDK2", response_class=HTMLResponse)
async def sample2():
    template = env.get_template('webview.html')
    return template.render()

@app.post("/sendResponse")
async def sendResponse():
    sender = 'id'
    reponse = "url"


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

    page.get_user_profile_sync(message.sender.id)
    # page.send(message.sender.id, "thank you! your message is '%s'" % message.text)
    buttons = [
        URLButton(title="Open Webview", url=(endpoint_url / "sampleMessagerSDK").url, messenger_extensions=True),
        PostbackButton(title="trigger Postback", payload="DEVELOPED_DEFINED_PAYLOAD"),
        CallButton(title="Call Phone Number", payload="+66992866936")
    ]
    print(message.sender.id)
    tan = Sender(id="3144004072361851")
    # content = ContentButton(
    #     text=f"replied to {message.text}",
    #     buttons=buttons,
    #     # quick_replies=[QuickReply(title='hi', payload='test')]
    # )
    # page.send(message.sender, content)
    # typing_fn = partial(page.typing_on, message.sender)
    # stop_typing_fn = partial(page.typing_off, message.sender)
    # await humanTyping.act_typing_simple(message.text, typing_fn, stop_typing_fn)
    await page.reply(message, content)
    # page.send(message.sender, content)
    # page._send(
    #

    #     )


@page.handle_postback
async def log(event: PostBackEvent):
    logger.info(f"{event.entry} ")


@page.handle_delivery
async def delivery(event: DeliveriesEvent):
    logger.info(f"{event.entry} ")


@page.callback(payloads=["test"], quick_reply=True, button=False)
async def log3(event):
    logger.info("log3")

if __name__ == "__main__":
    tan = Sender(id="3144004072361851")
    buttons1 = [
        URLButton(
            title="Open Webview",
            url="https://www.youtube.com/watch?v=riYzZrkOc3o",
            messenger_extensions=False
        ),
        PostbackButton(
            title="trigger Postback",
            payload="print is true"
        ),
        CallButton(
            title="Call Phone Number",
            payload="+66900622693"
        )
    ]
    content_button_template = ContentButton(
        text=f"replied to ",
        buttons=buttons1,
        quick_replies=None
    )
    # ------------------------------------------------------------------- #
    default_act = DefaultAction(
        # url="https://www.youtube.com/watch?v=jrOUGFFtMCw",
        # fallback_url="https://frankonfraud.com/wp-content/uploads/2018/11/fallback-fraud-in-us.jpg"
        url="https://www.youtube.com/watch?v=jrOUGFFtMCw",
    )
    buttons2 = [
        LogInButton(
            url="https://www.youtube.com/watch?v=riYzZrkOc3o",
        ),
        LogOutButton(
        )
    ]
    gallery = [
        GenericElements(
            title="Welcome to Generic (/w DA)",
            subtitle="subtitle is here!",
            image_url="https://www.biospectrumasia.com/uploads/articles/is-japan-changing-its-attitude-towards"
                      "-generic-drugs.jpg",
            default_action=default_act,
            buttons=None
        ),
        GenericElements(
            title="Button Test",
            subtitle="Log I/O sub-",
            image_url="https://www.biospectrumasia.com/uploads/articles/is-japan-changing-its-attitude-towards"
                      "-generic-drugs.jpg",
            default_action=DefaultAction(
                url="https://developers.facebook.com/docs/messenger-platform/reference/templates/generic#elements"
            ),
            buttons=buttons2
        )
    ]
    content_generic_template = ContentGeneric(
        elements=gallery,
        image_aspect_ratio="square",  # "horizontal" or "square"
        quick_replies=None
    )
    # ------------------------------------------------------------------- #
    buttons3 = [
        URLButton(
            title="What is this?!?!",
            url="https://www.facebook.com/sirote.klampaiboon/photos/a.373530246050409/4230721946997867/"
        )
    ]
    buttons4 = [
        URLButton(
            title="What is this?!?!",
            url="https://www.republicworld.com/entertainment-news/whats-viral/video-of-squirrel-asking-for-water"
                "-leaves-netizens-heartbroken-watch.html "
        ),
        URLButton(
            title="Original",
            url="https://www.facebook.com/1588173658083515/videos/301934891007397/"
        )
    ]
    media1 = [
        MediaElements(
            media_type="image",
            url="https://www.facebook.com/sirote.klampaiboon/photos/a.373530246050409/4230721946997867/",
            buttons=buttons3
        )
    ]
    media2 = [
        MediaElements(
            media_type="video",
            url="https://www.facebook.com/1588173658083515/videos/301934891007397/",
            buttons=buttons4
        )
    ]
    content_media_image_template = ContentMedia(
        elements=media1,
        sharable=False,  # Visible next to the content in mobile messenger
        quick_replies=None
    )
    content_media_video_template = ContentMedia(
        elements=media2,
        sharable=True,
        quick_replies=None
    )
    # ------------------------------------------------------------------- #
    address_rec = Address(
        street_1="Address 1",
        street_2="Address 2",
        city="City",
        postal_code="10140",
        state="state",
        country="country",
    )
    summary_rec = Summary(
        subtotal=75.00,
        shipping_cost=4.95,
        total_tax=6.19,
        total_cost=56.14,
    )
    adjustments_rec = [
        Adjustments(
            name="New Customer Discount",
            amount=20
        ),
        Adjustments(
            name="$10 Off Coupon",
            amount=10
        )
    ]
    receipt_element = [
        ReceiptElements(
            title="Elements are here!",
            subtitle="this on is for FREE!!!",
            quantity=2,
            price=50.00,
            currency="USD",
            image_url="https://www.pngjoy.com/pngs/96/2010071_residentsleeper-wutface-emote-png-download.png"
        ),
        ReceiptElements(
            title="!Worker require here!",
            subtitle="Want someone to carry on",
            quantity=1,
            price=25.00,
            currency="USD",
            image_url="https://www.pngjoy.com/pngs/96/2010071_residentsleeper-wutface-emote-png-download.png"
        )
    ]
    content_receipt_template = ContentReceipt(
        sharable=True,
        recipient_name="Someone Special",
        merchant_name=None,
        order_number="12345678902",
        currency="USD",
        payment_method="Visa 1234",  # This can be a custom string, such as, "Visa 1234".
        timestamp="1428444852",
        elements=receipt_element,
        address=address_rec,
        summary=summary_rec,
        adjustments=adjustments_rec,
        quick_replies=None,
    )
    # ------------------------------------------------------------------- #
    page.send(tan, content_button_template)
    # page.send(tan, content_generic_template)
    # page.send(tan, content_media_image_template)
    # page.send(tan, content_media_video_template)
    # page.send(tan, content_receipt_template)
    # page.send(message.sender, content)
    # typing_fn = partial(page.typing_on, message.sender)
    # stop_typing_fn = partial(page.typing_off, message.sender)
    # await humanTyping.act_typing_simple(message.text, typing_fn, stop_typing_fn)
    # page.reply(message, content)
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True, log_level='debug')

