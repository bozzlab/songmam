from typing import Optional, Literal

from pydantic import BaseModel

from songmam.facebook.entries.base import MessagingWithTimestamp

class Referral(BaseModel):
    ref: str
    source: Literal["MESSENGER_CODE", "DISCOVER_TAB", "ADS", "SHORTLINK", "CUSTOMER_CHAT_PLUGIN"]
    type: str
    ad_id: Optional[str]
    referer_uri: Optional[str]


class ReferralEntry(MessagingWithTimestamp):
    referral: Referral

# {
#     "recipient": {
#         "id": "<PSID>"
#     },
#     "recipient": {
#         "id": "<PAGE_ID>"
#     },
#     "timestamp": 1458692752478,
#     "referral": {
#                     "ref": < REF_DATA_PASSED_IN_M.ME_PARAM >,
#     "source": "SHORTLINK",
#     "type": "OPEN_THREAD",
# }
# }