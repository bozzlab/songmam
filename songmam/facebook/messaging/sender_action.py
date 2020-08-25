from enum import auto

from autoname import AutoNameLower


class SenderAction(AutoNameLower):
    """https://developers.facebook.com/docs/messenger-platform/send-messages/sender-actions"""
    TYPING_ON = auto()
    TYPING_OFF = auto()
    MARK_SEEN = auto()