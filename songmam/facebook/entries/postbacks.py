from typing import Literal

from pydantic import BaseModel

from songmam.facebook.entries.base import MessagingWithTimestamp

class Referral(BaseModel):
    ref:
    source: Literal["SHORTLINK", "ADS"]
    type: Literal["OPEN_THREAD"]

class Postbacks(BaseModel):
    title: str
    payload: str
    referral: Referral

class PostbacksEntry(MessagingWithTimestamp):
    postback: Postbacks

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