# __version__ = '2.5.0'

# from .page import *
from .middleware import VerificationMiddleware
from songmam.facebook.webhook import Webhook
from .facebook.entries.message import attachment as Attachment

# from songmam.middleware import VerificationMiddleware
# from songmam import VerificationMiddleware