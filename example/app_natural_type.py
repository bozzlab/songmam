from functools import partial

from fastapi import FastAPI


from songmam import Webhook
from songmam.api.events import MessageEvent
from songmam.api.content import ContentButton

from songmam.humanTyping import HumanTyping
from songmam.page import Page




page = Page()
app = FastAPI()
humanTyping =HumanTyping()


page.add_verification_middleware(app)


@app.post("/webhook")
async def handle_entry(webhook: Webhook):
    await page.handle_webhook(webhook)
    return "ok"



@page.handle_message
async def echo(message: MessageEvent):

    content = ContentButton(
        text=f"replied to {message.text}",
    )
    typing_fn = partial(page.typing_on_sync, message.sender)
    stop_typing_fn = partial(page.typing_off_sync, message.sender)
    await humanTyping.act_typing_simple(message.text, typing_fn, stop_typing_fn)
    page.reply_sync(message, content)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True, log_level='debug')