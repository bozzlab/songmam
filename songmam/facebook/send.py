# https://developers.facebook.com/docs/messenger-platform/send-messages#send_api_basics
from pydantic import BaseModel
from typing import Optional, Literal, List

from songmam.facebook.entries.base import ThingWithID


class SendResponse(BaseModel):
    recipient_id: Optional[str]
    message_id: Optional[str]


class SendRecipient(BaseModel):
    id: ThingWithID
    user_ref: Optional[str]
    post_id: Optional[str]
    comment_id: Optional[str]


class MessageAttachmentPayload:
    # Payload of attachment, can either be
    # a Template Payload
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates#payload
    """
    template_type: Optional[str]
    # ...: Mixed ???
    # or
    # a File Attachment Payload
    """
    https://developers.facebook.com/docs/messenger-platform/reference/attachment-upload-api#payload
    """
    url: Optional[str]
    is_reusable: Optional[bool]


class MessageAttachment:
    """
    https://developers.facebook.com/docs/messenger-platform/reference/send-api/#attachment
    """
    type: Optional[str]
    payload: Optional[MessageAttachmentPayload]


class SendMessage(BaseModel):
    text: Optional[str]
    attachment: Optional[MessageAttachment]
    quick_replies: Optional[List[str]] # Array<quick_reply>
    metadata: Optional[str]


class RequestUriEntry(BaseModel):
    messaging_type: Optional[Literal["RESPONSE", "UPDATE", "MESSAGE_TAG"]]
    recipient: Optional[SendRecipient]
    message: Optional[SendMessage]
    sender_action: Optional[Literal["typing_on", "typing_off", "mark_seen"]] # confused by description
    notification_type: Optional[str]
    tag: Optional[str]
