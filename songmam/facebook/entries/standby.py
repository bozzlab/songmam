from pydantic import BaseModel

from songmam.webhook import Webhook

class StandbyEntry(BaseModel):
    id: str
    time: int
    standby: List[]

class StandbyObject(Webhook):
    entry: StandbyEntry

# {
#   "object":"page",
#   "entry":[
#     {
#       "id":"<PAGE_ID>",
#       "time":1458692752478,
#       "standby":[
#         {
#           "sender":{
#             "id":"<USER_ID>"
#           },
#           "recipient":{
#             "id":"<PAGE_ID>"
#           },
#
#           ...
#         }
#       ]
#     }
#   ]
# }