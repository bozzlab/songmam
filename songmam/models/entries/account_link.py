from typing import Literal

from pydantic import BaseModel

from songmam.models.entries.base import WithTimestamp


class AccountLink(BaseModel):
    status: Literal["linked", "unlinked"]
    authorization_code: str

class AccountLinkEntry(WithTimestamp):
    account_linking: AccountLink

# {
#   "recipient":{
#     "id":"USER_ID"
#   },
#   "recipient":{
#     "id":"PAGE_ID"
#   },
#   "timestamp":1234567890,
#   "account_linking":{
#     "status":"linked",
#     "authorization_code":"PASS_THROUGH_AUTHORIZATION_CODE"
#   }
# }