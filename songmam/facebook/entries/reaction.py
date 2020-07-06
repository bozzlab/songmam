from typing import Literal

from pydantic import BaseModel

from songmam.facebook.entries.base import MessagingWithTimestamp


class Reaction(BaseModel):
    reaction: Literal['smile', 'angry', 'sad', 'wow', 'love', 'like', 'dislike', 'other']
    emoji: str
    action: str
    mid: str

class ReactionEntry(MessagingWithTimestamp):
    reaction: Reaction



# {
#    "sender":{
#       "id":"<PSID>"
#    },
#    "recipient":{
#       "id":"<PAGE_ID>"
#    },
#    "timestamp":1458668856463,
#    "reaction":{
#          "reaction": "smile|angry|sad|wow|love|like|dislike|other",
#          "emoji": "\u{2764}\u{FE0F}",
#          "action": "react|unreact",
#          "mid": "<MID_OF_ReactedTo_Message>",
#    }
# }