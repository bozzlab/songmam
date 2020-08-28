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


# Send a message
how to send a message from facebook page to user

### Basic



##### Image
jpg, png, gif support
```python
page.send_sync(recipient_id, Attachment.Image(image_url))
```


##### Audio
```python
page.send_sync(recipient_id, Attachment.Audio(audio_url))
```

##### Video
```python
page.send_sync(recipient_id, Attachment.Video(video_url))
```


##### File
```python
page.send_sync(recipient_id, Attachment.File(file_url))
```



##### quick reply
```python
quick_replies = [
  QuickReply(title="Action", payload="PICK_ACTION"),
  QuickReply(title="Comedy", payload="PICK_COMEDY")
]

# you can use a dict instead of a QuickReply class
#
# quick_replies = [{'title': 'Action', 'payload': 'PICK_ACTION'},
#                {'title': 'Comedy', 'payload': 'PICK_COMEDY'}]


page.send_sync(recipient_id, 
          "What's your favorite movie genre?",
          quick_replies=quick_replies,
          metadata="DEVELOPER_DEFINED_METADATA")
```

##### quick reply callback
you can define easily a quick reply callback method.
```python
@page.add_postback_handler(['PICK_ACTION', 'PICK_COMEDY'])
def callback_picked_genre(payload, event):
  print(payload, event)
  
# Also supported regex, it works corretly
# @page.add_postback_handler(['PICK_(.+)'])
```

if you want to handle only quick_reply callback without button postback
```python
@page.add_postback_handler(['PICK_ACTION', 'PICK_COMEDY'], types=['QUICK_REPLY'])
```

##### typing on/off
```python
page.typing_on_sync(recipient_id)
page.typing_off_sync(recipient_id)
```



### Templates

##### Template : Button
```python
buttons = [
  Templates.ButtonWeb("Open Web URL", "https://www.oculus.com/en-us/rift/"),
  Templates.ButtonPostBack("trigger Postback", "DEVELOPED_DEFINED_PAYLOAD"),
  Templates.ButtonPhoneNumber("Call Phone Number", "+16505551234")
]

# you can use a dict instead of a Button class
#
# buttons = [{'type': 'web_url', 'title': 'Open Web URL', 'value': 'https://www.oculus.com/en-us/rift/'},
#          {'type': 'postback', 'title': 'trigger Postback', 'value': 'DEVELOPED_DEFINED_PAYLOAD'},
#          {'type': 'phone_number', 'title': 'Call Phone Number', 'value': '+16505551234'}]

page.send_sync(recipient_id, Template.Button("hello", buttons))
```

##### button callback
you can define easily a button postback method (it works only postback type buttons).
```python
@page.add_postback_handler(['DEVELOPED_DEFINED_PAYLOAD'])
def callback_clicked_button(payload, event):
  print(payload, event)
  
# Also supported regex, it works corretly
# @page.add_postback_handler(['DEVELOPED_DEFINE(.+)'])
```

if you want to handle only button's postback without quick_reply callback
```python
@page.add_postback_handler(['DEVELOPED_DEFINED_PAYLOAD'], types=['POSTBACK'])
```


##### Template : Generic
```python
page.send_sync(recipient_id, Template.Generic([
  Template.GenericElement("rift",
                          subtitle="Next-generation virtual reality",
                          item_url="https://www.oculus.com/en-us/rift/",
                          image_url=CONFIG['SERVER_URL'] + "/assets/rift.png",
                          buttons=[
                              Template.ButtonWeb("Open Web URL", "https://www.oculus.com/en-us/rift/"),
                              Template.ButtonPostBack("tigger Postback", "DEVELOPED_DEFINED_PAYLOAD"),
                              Template.ButtonPhoneNumber("Call Phone Number", "+16505551234")
                          ]),
  Template.GenericElement("touch",
                          subtitle="Your Hands, Now in VR",
                          item_url="https://www.oculus.com/en-us/touch/",
                          image_url=CONFIG['SERVER_URL'] + "/assets/touch.png",
                          buttons=[
                              Template.ButtonWeb("Open Web URL", "https://www.oculus.com/en-us/rift/"),
                              Template.ButtonPostBack("tigger Postback", "DEVELOPED_DEFINED_PAYLOAD"),
                              Template.ButtonPhoneNumber("Call Phone Number", "+16505551234")
                          ])
]))
```


##### Template : Receipt
```python
    element = Template.ReceiptElement(title="Oculus Rift",
                                      subtitle="Includes: headset, sensor, remote",
                                      quantity=1,
                                      price=599.00,
                                      currency="USD",
                                      image_url=CONFIG['SERVER_URL'] + "/assets/riftsq.png"
                                      )

    address = Template.ReceiptAddress(street_1="1 Hacker Way",
                                      street_2="",
                                      city="Menlo Park",
                                      postal_code="94025",
                                      state="CA",
                                      country="US")

    summary = Template.ReceiptSummary(subtotal=698.99,
                                      shipping_cost=20.00,
                                      total_tax=57.67,
                                      total_cost=626.66)

    adjustment = Template.ReceiptAdjustment(name="New Customer Discount", amount=-50)

    page.send_sync(recipient_id, Template.Receipt(recipient_name='Peter Chang',
                                            order_number='1234',
                                            currency='USD',
                                            payment_method='Visa 1234',
                                            timestamp="1428444852",
                                            elements=[element],
                                            address=address,
                                            summary=summary,
                                            adjustments=[adjustment]))
```
### Options

##### notification type
support notification_type as a option

`NotificationType.REGULAR (default)`, `NotificationType.SILENT_PUSH`, `NotificationType.NO_PUSH`

```
page.send(recipient_id, 'hello', notification_type=NotificationType.NO_PUSH)
```
##### callback
you can set a callback function to each `page.send`
```
def callback(payload, response):
  print('response : ' + response.text)
  
page.send(recipient_id, 'hello', callback=callback)
```

# Thread settings
### Greeting text
```python
page.greeting("Welcome!")
```

### Get started button
```python
page.show_starting_button("START_PAYLOAD")

@page.add_postback_handler(['START_PAYLOAD'])
def start_callback(payload, event):
  print("Let's start!")
```

### Persistent menu
```python
page.show_persistent_menu([Template.ButtonPostBack('MENU1', 'MENU_PAYLOAD/1'),
                           Template.ButtonPostBack('MENU2', 'MENU_PAYLOAD/2')])

@page.add_postback_handler(['MENU_PAYLOAD/(.+)'])
def click_persistent_menu(payload, event):
  click_menu = payload.split('/')[1]
  print("you clicked %s menu" % click_menu)
```

# Fetch user/page profile
```
page_id = page.page_id
page_name = page.page_name
user_profile = page.get_user_profile(event.sender_id) # return dict
print(user_profile)

#{"first_name":"...", "last_name":"...", "profile_pic":"...", "locale":"...", "timezone":9, "gender":"..."}
```

# Example

1. fill example/config.py
2. run server
```bash
cd example
virtualenv env
source env/bin/activate
pip install -r requirements.txt
python server.py
```
