from typing import Literal, Optional, List

from pydantic import BaseModel

from songmam.facebook.entries.base import MessagingWithTimestamp
from songmam.facebook.entries.echo import Message
from songmam.facebook.entries.messages import MessageEntry, Messaging


class PostbackReferral(BaseModel):
    ref: str
    source: Literal["SHORTLINK", "ADS"]
    type: Literal["OPEN_THREAD"]

class Postback(BaseModel):
    title: str
    payload: str
    referral: Optional[PostbackReferral]

class PostbackMessaging(Messaging):
    message: Optional[Message]
    postback: Postback

class PostbackEntry(MessageEntry):
    # message: Optional[Message]
    messaging: List[PostbackMessaging]
    # postback: Optional[Postback]

# {
#   "sender":{
#     "id":"<PSID>"
#   },
#   "recipient":{
#     "id":"<PAGE_ID>"
#   },
#   "timestamp":1458692752478,
#   "postback":{
#     "title": "<TITLE_FOR_THE_CTA>",
#     "payload": "<USER_DEFINED_PAYLOAD>",
#     "referral": {
#       "ref": "<USER_DEFINED_REFERRAL_PARAM>",
#       "source": "<SHORTLINK>",
#       "type": "OPEN_THREAD",
#     }
#   }
# }

"""
{"object":"page","entry":[{"id":"103157244728633","time":1595061969020,"messaging":[{"sender":{"id":"2892682217518683"},"recipient":{"id":"103157244728633"},"timestamp":1595061968847,"postback":{"title":"menu 2","payload":"menu 2"}}]}]}
"""