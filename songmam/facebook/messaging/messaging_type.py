from enum import auto

from songmam.utils import AutoName


class MessagingType(AutoName):
    RESPONSE = auto()
    UPDATE = auto()
    MESSAGE_TAG = auto()
