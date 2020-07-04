from pydantic import BaseModel

from songmam.facebook.entries.base import ThingWithID


class PolicyEnforcement(BaseModel):
    action: str
    reason: str

class PolicyEnforcementEntry(BaseModel):
    recipitent: ThingWithID
    timestamp: int
    policy-enforcement: PolicyEnforcement

# {
#   "recipient": {
#     "id": "PAGE_ID"
#   },
#   "timestamp": 1458692752478,
#   "policy-enforcement": {
#     "action": "block",
#     "reason": "The bot violated our Platform Policies (https://developers.facebook.com/policy/#messengerplatform). Common violations include sending out excessive spammy messages or being non-functional."
#   }
# }