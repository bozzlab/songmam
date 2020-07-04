# __version__ = '2.5.0'

from .page import *
from .middleware import VerificationMiddleware
from .webhook import Webhook
from .facebook.entries.message import attachment as Attachment
from . import template as Template
