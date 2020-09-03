# import asyncio
# import json
# import re
# import hmac
# import hashlib
# from functools import partial
# from typing import Union, Optional, Literal, Set, List, Type, Awaitable
#
# import httpx
# import requests
# from cacheout import Cache
# from fastapi import FastAPI, Request
# from furl import furl
# from loguru import logger
# from pydantic import HttpUrl
# from songmam.models.messaging.quick_replies import QuickReply
# from songmam.models.messaging.templates import Message, AllButtonTypes, TemplateAttachment, PayloadButtonTemplate
# from auto_avajana.bubbling import Bubbling
#
# from .api.events import MessageEvent, PostBackEvent, MessagingReferralEvent, MessageDeliveriesEvent
# from .models import ThingWithId
# from .models.events.deliveries import MessageDeliveriesEvent
# from .models.events.echo import EchoEntry
# from .models.events.messages import MessagesEvent, Sender
# from .models.events.postback import PostbackEvent
# from .models.events.referral import ReferralMessaging
# from .models.messaging.message_tags import MessageTag
# from .models.messaging.messaging_type import MessagingType
# from .models.messaging.notification_type import NotificationType
# from .models.messaging.payload import CompletePayload, SenderActionPayload
# from songmam.models.messenger_profile.persistent_menu import UserPersistentMenu, MenuPerLocale
# from .models.messaging.sender_action import SenderAction
# from .models.messaging.templates.generic import GenericElement, PayloadGeneric
# from .models.messaging.templates.media import MediaElement, PayloadMedia
# from .models.messenger_profile import MessengerProfileProperty, MessengerProfile, GreetingPerLocale, GetStarted
# from .models.page import Page
# from .models.persona import Persona, PersonaWithId, PersonaResponse, AllPerosnasResponse, PersonaDeleteResponse
# from .models.send import SendResponse, SendRecipient
# from .models.user_profile import UserProfile
# from songmam.models.webhook import Webhook
#
# # See https://developers.facebook.com/docs/graph-api/changelog
# SUPPORTED_API_VERS = Literal[
#     "v7.0"  # May 5, 2020
# ]
#
#
# class Page:
#     access_token: str
#     verify_token: Optional[str] = None
#     app_secret: Optional[str] = None
#     api_version: SUPPORTED_API_VERS = 'v7.0'
#
#     page: Optional[Page] = None
#
#     def __init__(self, *,
#                  auto_mark_as_seen: bool = True,
#                  access_token: Optional[str] = None,
#                  verify_token: Optional[str] = None,
#                  app_secret: Optional[str] = None,
#                  persistent_menu: Optional[List[MenuPerLocale]] = None,
#                  greeting: Optional[List[GreetingPerLocale]] = None,
#                  get_started: Optional[GetStarted] = None,
#                  whitelisted_domains: Optional[List[HttpUrl]] = None,
#                  skip_quick_reply: bool = True,
#                  prevent_repeated_reply: bool = True,
#                  emu_type: bool = False
#                  ):
#         self.bubbling = Bubbling()
#
#         # Non-Dynamic Change
#         self.prevent_repeated_reply = prevent_repeated_reply
#         if prevent_repeated_reply:
#             self.reply_cache = Cache(maxsize=10000, ttl=60 * 15, default=None)
#
#         self.skip_quick_reply = skip_quick_reply
#         self.auto_mark_as_seen = auto_mark_as_seen
#
#         if access_token:
#             self.access_token = access_token
#         else:
#             raise Exception("access_token is required.")
#
#         self.verify_token = verify_token
#         if self.verify_token:
#             logger.warning("Without verify token, It is possible for your bot server to be substituded by hackers' server.")
#         self.app_secret = app_secret
#
#
#         # if persistent_menu or greeting or whitelisted_domains or get_started:
#         #     profile = MessengerProfile()
#         #
#         #     if persistent_menu:
#         #         profile.persistent_menu = persistent_menu
#         #     if greeting:
#         #         profile.greeting = greeting
#         #     if whitelisted_domains:
#         #         profile.whitelisted_domains = whitelisted_domains
#         #     if get_started:
#         #         profile.get_started = get_started
#         #
#         #     self._set_profile_property_sync(profile)
#
#         self.emu_type = emu_type
#         # self._after_send = options.pop('after_send', None)
#         # self._api_ver = options.pop('api_ver', 'v7.0')
#         # if self._api_ver not in SUPPORTED_API_VERS:
#         #     raise ValueError('Unsupported API Version : ' + self._api_ver)
#
#
#
#
#
#
