from decouple import config
from fastapi import FastAPI
from loguru import logger

# os.environ['PAGE_ACCESS_TOKEN'] = "MY Access token"
# os.environ['PAGE_VERIFY_TOKEN'] = "MY Verify token"
from songmam import WebhookHandler, MessengerApi
from songmam.models.messaging.quick_replies import QuickReply
from songmam.models.messaging.templates.button import PostbackButton
from songmam.models.webhook.events import *

app = FastAPI()
handler = WebhookHandler(app)
api = MessengerApi(config("PAGE_ACCESS_TOKEN"), auto_avajana=False)


@handler.add(MessagesEvent)
async def echo(event: MessagesEvent, *args, **kwargs):
    print(
        event.theMessaging.recipient,
        event.theMessaging.sender,
        event.theMessaging.message.text,
    )
    await api.send(
        event.sender,
        text=event.theMessaging.message.text,
        buttons=PostbackButton(title="send postback", payload="handlers.do:tell_user"),
        quick_replies=QuickReply(title="quick reply", payload="handlers.do:tell_user"),
    )


@handler.add(MessagesEventWithQuickReply)
async def echo2(entry: MessagesEventWithQuickReply, *args, **kwargs):
    logger.info("echo2")


@handler.add(MessagingReferralEvent)
async def handle_ref(entry: MessagingReferralEvent, *args, **kwargs):
    logger.info(entry.sender)
    logger.info(entry.ref)


@handler.add(MessageReadsEvent)
async def handle_read(entry: MessageReadsEvent, *args, **kwargs):
    logger.info(entry)


@handler.add(MessageDeliveriesEvent)
async def handle_delivery(entry: MessageDeliveriesEvent, *args, **kwargs):
    logger.info(entry)


# @handler.set_uncaught_postback_handler
# async def handle_uncaught_postback(event):
#     logger.info(event)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8002, reload=True, log_level="debug")
