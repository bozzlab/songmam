import json
import re
import hmac
import hashlib
from typing import Union, Optional, Literal, Set, List, Type

import httpx
import requests
from cacheout import Cache
from decouple import config, UndefinedValueError
from fastapi import FastAPI, Request
from furl import furl
from loguru import logger
from pydantic import HttpUrl

from .api.content import ContentButton, ContentGeneric, ContentMedia, ContentReceipt
from .api.events import MessageEvent, PostBackEvent, ReferralEvent, DeliveriesEvent
from .facebook import ThingWithId
from .facebook.entries.deliveries import DeliveriesEntry
from .facebook.entries.echo import EchoEntry
from .facebook.entries.messages import MessageEntry, Sender
from .facebook.entries.postback import PostbackEntry
from .facebook.entries.referral import ReferralEntry
from .facebook.messaging.message_tags import MessageTag
from .facebook.messaging.payload import BasePayload, SenderActionPayload
from songmam.facebook.messenger_profile.persistent_menu import UserPersistentMenu, MenuPerLocale
from .facebook.messaging.sender_action import SenderAction
from .facebook.messenger_profile import MessengerProfileProperty, MessengerProfile, GreetingPerLocale
from .facebook.page import Me
from .facebook.send import SendResponse, SendRecipient
from .facebook.user_profile import UserProfile
from songmam.facebook.webhook import Webhook

# See https://developers.facebook.com/docs/graph-api/changelog
SUPPORTED_API_VERS = Literal[
    "v7.0"  # May 5, 2020
]


class Page:
    access_token: str
    verify_token: Optional[str] = None
    app_secret: Optional[str] = None
    api_version: SUPPORTED_API_VERS = 'v7.0'

    page: Optional[Me] = None

    def __init__(self, *,
                 auto_mark_as_seen: bool = True,
                 access_token: Optional[str] = None,
                 verify_token: Optional[str] = None,
                 app_secret: Optional[str] = None,
                 persistent_menu: Optional[List[MenuPerLocale]] = None,
                 greeting: Optional[List[GreetingPerLocale]] = None,
                 whitelisted_domains: Optional[List[HttpUrl]] = None,
                 skip_quick_reply: bool = True,
                 prevent_repeated_reply: bool = True,
                 ):
        # Non-Dynamic Change
        self.prevent_repeated_reply = prevent_repeated_reply
        if prevent_repeated_reply:
            self.reply_cache = Cache(maxsize=10000, ttl=60 * 15, default=None)

        self.skip_quick_reply = skip_quick_reply
        self.auto_mark_as_seen = auto_mark_as_seen

        if access_token:
            self.access_token = access_token
        else:
            self.access_token = config("PAGE_ACCESS_TOKEN")

        if verify_token:
            self.verify_token = verify_token
        else:
            try:
                self.verify_token = config("PAGE_VERIFY_TOKEN")
            except UndefinedValueError:
                # value is None by default
                pass

        if app_secret:
            self.app_secret = app_secret
        else:
            try:
                self.app_secret = config("APP_SECRET")
            except UndefinedValueError:
                # value is None by default
                pass

        if persistent_menu or greeting:
            profile = MessengerProfile()

            if persistent_menu:
                profile.persistent_menu = persistent_menu
            if greeting:
                profile.greeting = greeting
            if whitelisted_domains:
                profile.whitelisted_domains = whitelisted_domains

            self._set_profile_property_sync(profile)

        # self._after_send = options.pop('after_send', None)
        # self._api_ver = options.pop('api_ver', 'v7.0')
        # if self._api_ver not in SUPPORTED_API_VERS:
        #     raise ValueError('Unsupported API Version : ' + self._api_ver)

    _entryCaster = {
        MessageEntry: MessageEvent,
        PostbackEntry: PostBackEvent,
        ReferralEntry: ReferralEvent,
        DeliveriesEntry: DeliveriesEvent
    }

    # these are set by decorators or the 'set_webhook_handler' method
    _webhook_handlers = {}
    _webhook_handlers_sync = {}

    _quick_reply_callbacks = {}
    _button_callbacks = {}
    _delivered_callbacks = {}

    _quick_reply_callbacks_key_regex = {}
    _button_callbacks_key_regex = {}
    _delivered_callbacks_key_regex = {}

    _after_send = None

    @property
    def base_api_furl(self) -> furl:
        furl_url = furl("https://graph.facebook.com/") / self.api_version
        # furl_url.args['access_token'] = self.access_token
        return furl_url

    def add_verification_middleware(self, app: FastAPI):
        from songmam import VerificationMiddleware
        app.add_middleware(VerificationMiddleware, verify_token=self.verify_token)

    def handle_webhook_sync(self, webhook: Webhook):
        for entry in webhook.entry:
            handler = self._webhook_handlers_sync.get(type(entry.theMessaging))
            if handler:
                handler(MessageEvent(entry))
            else:
                logger.warning("there's no {} handler", type(entry.theMessaging))

    async def handle_webhook(self, webhook: Webhook, *, request: Optional[Request] = None):

        # TODO: Convert this to middleware
        # Do the Webhook validation
        # https://developers.facebook.com/docs/messenger-platform/webhook#security
        if self.app_secret and request:
            header_signature = request.headers['X-Hub-Signature']
            if len(header_signature) == 45 and header_signature.startswith('sha1='):
                header_signature = header_signature[5:]
            else:
                raise NotImplementedError("Dev: how to handle this?")

            body = await request.body()
            expected_signature = hmac.new(self.app_secret, body, hashlib.sha1)

            if expected_signature != header_signature:
                raise AssertionError('SIGNATURE VERIFICATION FAIL')

        for entry in webhook.entry:
            entry_type = type(entry)
            handler = self._webhook_handlers.get(entry_type)
            eventConstructor = self._entryCaster.get(entry_type)
            if handler:
                event = eventConstructor(entry)

                if entry_type is MessageEntry:
                    if self.auto_mark_as_seen:
                        self.mark_seen_sync(event.sender)

                    if event.is_quick_reply:
                        matched_callbacks = self.get_quick_reply_callbacks(event)
                        for callback in matched_callbacks:
                            await callback(event)

                elif entry_type is PostbackEntry:
                    matched_callbacks = self.get_postback_callbacks(event)
                    for callback in matched_callbacks:
                        await callback(event)
                elif entry_type is ReferralEntry:
                    pass

                elif entry_type is DeliveriesEntry:
                    pass

                await handler(event)
            else:
                logger.warning("there's no {} handler", type(entry.theMessaging))

    @property
    def id(self):
        if self.page is None:
            self._fetch_page_info_sync()

        return self.page.id

    @property
    def name(self):
        if self.page is None:
            self._fetch_page_info_sync()

        return self.page.name

    def _fetch_page_info_sync(self):
        r = requests.get(self.base_api_furl / "me",
                         params={"access_token": self.access_token},
                         headers={'Content-type': 'application/json'})

        if r.status_code != requests.codes.ok:
            print(r.text)
            return

        self.page = Me.parse_raw(r.text)

    async def _fetch_page_info(self):
        async with httpx.AsyncClient(base_url=self.base_api_furl.url, headers={'Content-type': 'application/json'},
                                     params={"access_token": self.access_token}) as client:
            response = await client.get(
                f"/me"
            )

        if response.status_code != 200:
            raise Exception(response.text)

        self.page = Me.parse_raw(response.text)

    def get_user_profile_sync(self, fb_user_id) -> UserProfile:
        r = requests.get(self.base_api_furl / fb_user_id,
                         params={"access_token": self.access_token},
                         headers={'Content-type': 'application/json'})

        if r.status_code != requests.codes.ok:
            raise ConnectionError(r.text)

        user_profile = UserProfile.parse_raw(r.text)
        return user_profile


    async def get_user_profile(self, user: Type[ThingWithId]) -> UserProfile:
        async with httpx.AsyncClient(base_url=self.base_api_furl.url, headers={'Content-type': 'application/json'},
                                     params={"access_token": self.access_token}) as client:
            response = await client.get(
                f"/{user.id}"
            )

        if response.status_code != 200:
            raise Exception(response.text)

        user_profile = UserProfile.parse_raw(response.text)
        return user_profile


    def get_messenger_code(self, ref=None, image_size=1000):
        d = {}
        d['type'] = 'standard'
        d['image_size'] = image_size
        if ref:
            d['data'] = {'ref': ref}

        r = requests.post(self._api_uri("me/messenger_codes"),
                          params={"access_token": self.access_token},
                          json=d,
                          headers={'Content-type': 'application/json'})
        if r.status_code != requests.codes.ok:
            print(r.text)
            return None

        data = json.loads(r.text)
        if 'uri' not in data:
            raise ValueError('Could not fetch messener code : GET /' +
                             self.api_version + '/me')

        return data['uri']

    def _send_sync(self, payload: Union[BasePayload], callback_sync=None) -> SendResponse:
        f_url = self.base_api_furl / "me/messages"
        data = payload.json(exclude_none=True)
        response = requests.post(f_url.url,
                                 params={"access_token": self.access_token},
                                 data=data,
                                 headers={'Content-type': 'application/json'})

        if response.status_code != requests.codes.ok:
            print(response.text)

        if callback_sync is not None:
            callback_sync(payload, response)

        if self._after_send is not None:
            self._after_send(payload, response)

        return SendResponse.parse_raw(response.text)

    async def _send(self, payload: Union[BasePayload], callback=None) -> SendResponse:

        data = payload.json(exclude_none=True)

        async with httpx.AsyncClient(base_url=self.base_api_furl.url, headers={'Content-type': 'application/json'},
                                     params={"access_token": self.access_token}) as client:
            response = await client.post(
                "/me/messages",
                data=data,
            )

        if response.status_code != 200:
            raise Exception(response.text)

        if callback is not None:
            await callback(payload, response)

        if self._after_send is not None:
            self._after_send(payload, response)

        return SendResponse.parse_raw(response.text)

    def send_sync(self, sender: Sender, message: Union[ContentButton, ContentGeneric, ContentMedia, ContentReceipt], *, quick_replies=None, metadata=None,
                  notification_type=None, tag: Optional[MessageTag] = None, callback_sync: Optional[callable] = None):

        return self._send_sync(
            BasePayload(
                recipient=sender,
                message=message.message
            ),
            callback_sync=callback_sync
        )

    async def send(self, sender: Sender, message: Union[ContentButton, ContentGeneric, ContentMedia, ContentReceipt], *, quick_replies=None, metadata=None,
                  notification_type=None, tag: Optional[MessageTag] = None, callback: Optional[callable] = None):

        return await self._send(
            BasePayload(
                recipient=sender,
                message=message.message
            ),
            callback=callback
        )

    def reply(self, message_to_reply_to: MessageEvent, message: ContentButton, *, quick_replies=None, metadata=None,
              notification_type=None, tag: Optional[MessageTag] = None, callback: Optional[callable] = None):

        if self.prevent_repeated_reply:
            message_id = message_to_reply_to.entry.theMessaging.message.mid
            if message_id not in self.reply_cache:
                # good to go
                self.reply_cache.set(message_id, True)
            else:
                logger.warning("Songmum prevented a message from being reply to the same event multiple times.")
                logger.warning(message_to_reply_to)
                return

        return self._send_sync(
            BasePayload(
                recipient=message_to_reply_to.sender,
                message=message.message
            ), callback_sync=callback)

    async def reply(self, message_to_reply_to: MessageEvent, message, *, quick_replies=None, metadata=None,
                    notification_type=None, tag: Optional[MessageTag] = None, callback: Optional[callable] = None):

        if self.prevent_repeated_reply:
            message_id = message_to_reply_to.entry.theMessaging.message.mid
            if message_id not in self.reply_cache:
                # good to go
                self.reply_cache.set(message_id, True)
            else:
                logger.warning("Songmum prevented a message from being reply to the same event multiple times.")
                logger.warning(message_to_reply_to)
                return

        return await self._send(
            BasePayload(
                recipient=message_to_reply_to.sender,
                message=message.message
            ),
            callback=callback
        )

    def typing_on_sync(self, recipient: Type[ThingWithId]):
        payload = SenderActionPayload(recipient=recipient,
                                      sender_action=SenderAction.TYPING_ON)

        self._send_sync(payload)

    async def typing_on(self, recipient: Type[ThingWithId]):
        payload = SenderActionPayload(recipient=recipient,
                                      sender_action=SenderAction.TYPING_ON)

        return await self._send(payload)

    def typing_off_sync(self, recipient: Type[ThingWithId]):
        payload = SenderActionPayload(recipient=recipient,
                                      sender_action=SenderAction.TYPING_OFF)

        self._send_sync(payload)

    async def typing_off(self, recipient: Type[ThingWithId]):
        payload = SenderActionPayload(recipient=recipient,
                                      sender_action=SenderAction.TYPING_OFF)

        return await self._send(payload)

    def mark_seen_sync(self, recipient: Type[ThingWithId]):
        payload = SenderActionPayload(recipient=recipient,
                                      sender_action=SenderAction.MARK_SEEN)

        self._send_sync(payload)

    async def mark_seen(self, recipient: Type[ThingWithId]):
        payload = SenderActionPayload(recipient=recipient,
                                      sender_action=SenderAction.MARK_SEEN)

        return await self._send(payload)

    """
    messenger profile (see https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api)
    """

    def _set_profile_property_sync(self, data: MessengerProfile):

        f_url = self.base_api_furl / "me" / "messenger_profile"
        r = requests.post(f_url.url,
                          params={"access_token": self.access_token},
                          data=data.json(exclude_none=True),
                          headers={'Content-type': 'application/json'})

        if r.status_code != requests.codes.ok:
            raise Exception(r.text)

    def _del_profile_property_sync(self, properties: Set[MessengerProfileProperty]):
        f_url = self.base_api_furl / "me" / "messenger_profile"
        r = requests.delete(f_url.url,
                            params={"access_token": self.access_token},
                            data=json.dumps({
                                'fields': [p.value for p in properties]
                            }),
                            headers={'Content-type': 'application/json'})

        if r.status_code != requests.codes.ok:
            logger.error("Facebook Server replied" + r.text)
            raise Exception(r.text)

    """
    Custom User Settings
    """

    def get_user_settings(self, user_id: str):
        f_url = self.base_api_furl / 'me' / 'custom_user_settings'
        params = {
            "access_token": self.access_token,
            "psid": user_id
        }
        r = requests.get(f_url.url,
                         params=params)

        if r.status_code != requests.codes.ok:
            raise Exception(r.text)

        # TODO: create object for this GET Request https://developers.facebook.com/docs/messenger-platform/send-messages/persistent-menu
        return r.json()

    def set_user_menu(self, sender: Type[ThingWithId], menus: List[MenuPerLocale]):
        if isinstance(menus, MenuPerLocale):
            menus = [menus]

        f_url = self.base_api_furl / 'me' / 'custom_user_settings'
        r = requests.post(f_url.url,
                          params={"access_token": self.access_token},
                          data=UserPersistentMenu(
                              psid=sender.id,
                              persistent_menu=menus
                          ).json(),
                          headers={'Content-type': 'application/json'})

        if r.status_code != requests.codes.ok:
            raise Exception(r.text)

    def _set_user_menu(self, payload: UserPersistentMenu):
        f_url = self.base_api_furl / 'me' / 'custom_user_settings'
        r = requests.post(f_url.url,
                          params={"access_token": self.access_token},
                          data=payload.json(),
                          headers={'Content-type': 'application/json'})

        if r.status_code != requests.codes.ok:
            raise Exception(r.text)

    def delete_user_menu(self, user_id: str):
        f_url = self.base_api_furl / 'me' / 'custom_user_settings'

        params = {
            "access_token": self.access_token,
            "psid": user_id,
            "params": "[%22persistent_menu%22]"
        }
        r = requests.delete(f_url.url,
                            params=params)

        if r.status_code != requests.codes.ok:
            raise Exception(r.text)

    """
    handlers and decorations
    """

    # def set_webhook_handler(self, scope, callback):
    #     """
    #     Allows adding a webhook_handler as an alternative to the decorators
    #     """
    #     scope = scope.lower()
    #
    #     if scope == 'after_send':
    #         self._after_send = callback
    #         return
    #
    #     if scope not in Page.WEBHOOK_ENDPOINTS:
    #         raise ValueError("The 'scope' argument must be one of {}.".format(Page.WEBHOOK_ENDPOINTS))
    #
    #     self._webhook_handlers[scope] = callback

    def handle_optin(self, func):
        self._webhook_handlers['optin'] = func

    def handle_message_sync(self, func: callable):
        self._webhook_handlers_sync[MessageEntry] = func

    def handle_message(self, func: callable):
        self._webhook_handlers[MessageEntry] = func

    def handle_echo_sync(self, func: callable):
        self._webhook_handlers_sync[EchoEntry] = func

    def handle_echo(self, func: callable):
        self._webhook_handlers[EchoEntry] = func

    def handle_delivery(self, func):
        self._webhook_handlers[DeliveriesEntry] = func

    def handle_postback_sync(self, func):
        self._webhook_handlers_sync[PostbackEntry] = func

    def handle_postback(self, func):
        self._webhook_handlers[PostbackEntry] = func

    # def handle_read(self, func):
    #     self._webhook_handlers['read'] = func
    #
    # def handle_account_linking(self, func):
    #     self._webhook_handlers['account_linking'] = func

    # def handle_referral_sync(self, func):
    #     self._webhook_handlers_sync['referral'] = func

    def handle_referral(self, func):
        self._webhook_handlers[ReferralEntry] = func
    #
    # def handle_game_play(self, func):
    #     self._webhook_handlers['game_play'] = func
    #
    # def handle_pass_thread_control(self, func):
    #     self._webhook_handlers['pass_thread_control'] = func
    #
    # def handle_take_thread_control(self, func):
    #     self._webhook_handlers['take_thread_control'] = func
    #
    # def handle_request_thread_control(self, func):
    #     self._webhook_handlers['request_thread_control'] = func
    #
    # def handle_app_roles(self, func):
    #     self._webhook_handlers['app_roles'] = func
    #
    # def handle_policy_enforcement(self, func):
    #     self._webhook_handlers['policy_enforcement'] = func
    #
    # def handle_checkout_update(self, func):
    #     self._webhook_handlers['checkout_update'] = func
    #
    # def handle_payment(self, func):
    #     self._webhook_handlers['payment'] = func
    #
    # def handle_standby(self, func):
    #     self._webhook_handlers['standby'] = func

    def after_send(self, func):
        self._after_send = func

    def callback(self, payloads=None, quick_reply=True, button=True):

        def wrapper(func):
            if payloads is None:
                return func

            for payload in payloads:
                if quick_reply:
                    self._quick_reply_callbacks[payload] = func
                if button:
                    self._button_callbacks[payload] = func

            return func

        return wrapper

    def get_quick_reply_callbacks(self, event: MessageEvent):
        callbacks = []
        for key in self._quick_reply_callbacks.keys():
            if key not in self._quick_reply_callbacks_key_regex:
                self._quick_reply_callbacks_key_regex[key] = re.compile(key + '$')

            if self._quick_reply_callbacks_key_regex[key].match(event.quick_reply.payload):
                callbacks.append(self._quick_reply_callbacks[key])

        return callbacks

    def get_postback_callbacks(self, event: PostBackEvent):
        callbacks = []
        for key in self._button_callbacks.keys():
            if key not in self._button_callbacks_key_regex:
                self._button_callbacks_key_regex[key] = re.compile(key + '$')

            if self._button_callbacks_key_regex[key].match(event.payload):
                callbacks.append(self._button_callbacks[key])

        return callbacks
