from pydantic import BaseModel

from songmam.facebook.entries.base import MessagingWithTimestamp

class Optin(BaseModel):
    ref: str
    user_ref: str

class OptinEntry(MessagingWithTimestamp):
    optin: Optin

# {
#   "recipient": {
#     "id": "<PSID>"
#   },
#   "recipient": {
#     "id": "<PAGE_ID>"
#   },
#   "timestamp": 1234567890,
#   "optin": {
#     "ref": "<PASS_THROUGH_PARAM>",
#     "user_ref": "<REF_FROM_CHECKBOX_PLUGIN>"
#   }
# }