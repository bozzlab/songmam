from decouple import config
from fastapi import FastAPI
from loguru import logger


# os.environ['PAGE_ACCESS_TOKEN'] = "MY Access token"
# os.environ['PAGE_VERIFY_TOKEN'] = "MY Verify token"
from songmam import WebhookHandler, MessengerApi
from songmam.models.webhook.events import *

app = FastAPI()
handler = WebhookHandler(
    app
)
api = MessengerApi(config('PAGE_ACCESS_TOKEN'))

@handler.add(MessagesEvent)
async def echo(entry: MessagesEvent):
    print(entry.theMessaging.recipient, entry.theMessaging.sender,entry.theMessaging.message.text)
    await api.send(entry.sender, text="hi")

@handler.add(MessagingReferralEvent)
async def handle_ref(entry: MessagingReferralEvent):
    logger.info(entry.sender)
    logger.info(entry.ref)

@handler.add(MessageReadsEvent)
async def handle_read(entry: MessageReadsEvent):
    logger.info(entry)

@handler.add(MessageDeliveriesEvent)
async def handle_delivery(entry: MessageDeliveriesEvent):
    logger.info(entry)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True, log_level='debug')