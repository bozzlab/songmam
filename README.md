# Since This repo is almost entirely change from the fork, contains a lot of remnants(releases,tags,docs,tests) that irrelevant to this library, and currently maintain by Codustry. new repo of songmam is here https://github.com/codustry/songmam.

# songmam


**songmam**, comes from 'ส่งแหม่' meaning SEND IT, is 
a Python Library For Using The Facebook Messenger Platform, *a fork of [fbmq](https://github.com/conbus/fbmq)*

## What's new in `songmam`
* production ready, fast, correct, fully typed
* parallel and in order code structure compare to facebook docs
* build for `fastapi`, fast, async, and auto documentation
* use [the latest API](https://developers.facebook.com/docs/graph-api/changelog/#graph-api-changelog) version v7.0
* add verify token mechanics
* beautiful docs

## RoadMap
See issue

## Alternatives
- fbbotw - https://github.com/JoabMendes/fbbotw


## Install
```
pip install songmam
```

## Quickstart
```python
import os
from fastapi import FastAPI
from songmam import Page, Webhook, MessageEvent

os.environ['PAGE_ACCESS_TOKEN'] = "MY Access token"
os.environ['PAGE_VERIFY_TOKEN'] = "MY Verify token"
# Alternatively this could be specify in .env

app = FastAPI()
page = Page()

page.add_verification_middleware(app)

@app.post("/webhook")
async def handle_entry(webhook: Webhook):
    await page.handle_webhook(webhook)
    return "ok"

@page.handle_message
def echo(message: MessageEvent):
    page.send_sync(message.sender.id, "thank you! your text is '%s'" % message.text)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True, log_level='debug')
```


