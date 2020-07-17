from typing import Optional

from pydantic import BaseModel

from songmam.facebook.entries.base import MessagingWithTimestamp
from songmam.facebook.entries.messages import MessageEntry, Message as Message_


class Message(Message_):
    is_echo: bool
    app_id: str
    metadata: Optional[str]

class EchoEntry(MessageEntry):
    message: Message

# {
#   "sender":{
#     "id":"<PSID>"
#   },
#   "recipient":{
#     "id":"<USER_ID>"
#   },
#   "timestamp":1457764197627,
#   "message":{
#     "is_echo":true,
#     "app_id":1517776481860111,
#     "metadata": "<DEVELOPER_DEFINED_METADATA_STRING>",
#     "mid":"mid.1457764197618:41d102a3e1ae206a38",
#     ...
#   }
# }