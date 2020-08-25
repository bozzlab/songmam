# __version__ = '2.5.0'

# from .page import *
from .middleware import VerificationMiddleware
from songmam.models.webhook import Webhook
from .models.entries.message import attachment as Attachment

# from songmam.middleware import VerificationMiddleware
# from songmam import VerificationMiddleware