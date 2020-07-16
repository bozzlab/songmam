# https://developers.facebook.com/docs/messenger-platform/send-messages#send_api_basics
from pydantic import BaseModel
from typing  import Optional



class SendResponse(BaseModel):
    recipient_id: Optional[str]
    message_id: str