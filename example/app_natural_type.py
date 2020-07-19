from functools import partial

from fastapi import FastAPI, Request


# os.environ['PAGE_ACCESS_TOKEN'] = "MY Access token"
# os.environ['PAGE_VERIFY_TOKEN'] = "MY Verify token"
from jinja2 import Environment, select_autoescape, FileSystemLoader
from loguru import logger

from songmam import Webhook
from songmam.api.events import MessageEvent, PostBackEvent
from songmam.api.content import Content

from songmam.humanTyping import HumanTyping
from songmam.page import Page




page = Page(
    whitelisted_domains=["https://e1bbfd3fd123.ngrok.io"],
)
app = FastAPI()
humanTyping =HumanTyping()


page.add_verification_middleware(app)


@app.post("/webhook")
async def handle_entry(webhook: Webhook, request: Request):
    await page.handle_webhook(webhook)
    return "ok"



@page.handle_message
async def echo(message: MessageEvent):

    content = Content(
        text=f"replied to {message.text}",
    )
    # page.send(message.sender, content)
    typing_fn = partial(page.typing_on, message.sender)
    stop_typing_fn = partial(page.typing_off, message.sender)
    await humanTyping.act_typing_simple(message.text, typing_fn, stop_typing_fn)
    page.reply(message, content)
    # page._send(
    #
    #     )


@page.handle_postback
async def log(event: PostBackEvent):
    logger.info(f"{event.entry} ")

@page.callback(payloads=["test"], quick_reply=True, button=False)
async def log3(event):
    logger.info("log3")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True, log_level='debug')