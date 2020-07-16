import json
import sys
import re
import hmac
import hashlib
import requests
from decouple import config, UndefinedValueError
from fastapi import FastAPI, Request
from furl import furl
from loguru import logger

from .api.events import MessageEvent, PostBackEvent
from .facebook.entries.messages import Messaging, MessageEntry
from .facebook.entries.postbacks import Postbacks, PostbacksEntry
from .facebook.page import Me
from .facebook.send import MessageTag, SendResponse
from .facebook.user_profile import UserProfile
from songmam.facebook.webhook import Webhook
from .payload import *
from .template import *

# See https://developers.facebook.com/docs/graph-api/changelog
SUPPORTED_API_VERS=[
    "v7.0" # May 5, 2020
]

# See https://developers.facebook.com/docs/messenger-platform/messenger-profile/supported-locales
SUPPORTED_LOCALES=[
    "default",
    "en_US",
    "ca_ES",
    "cs_CZ",
    "cx_PH",
    "cy_GB",
    "da_DK",
    "de_DE",
    "eu_ES",
    "en_UD",
    "es_LA",
    "es_ES",
    "gn_PY",
    "fi_FI",
    "fr_FR",
    "gl_ES",
    "hu_HU",
    "it_IT",
    "ja_JP",
    "ko_KR",
    "nb_NO",
    "nn_NO",
    "nl_NL",
    "fy_NL",
    "pl_PL",
    "pt_BR",
    "pt_PT",
    "ro_RO",
    "ru_RU",
    "sk_SK",
    "sl_SI",
    "sv_SE",
    "th_TH",
    "tr_TR",
    "ku_TR",
    "zh_CN",
    "zh_HK",
    "zh_TW",
    "af_ZA",
    "sq_AL",
    "hy_AM",
    "az_AZ",
    "be_BY",
    "bn_IN",
    "bs_BA",
    "bg_BG",
    "hr_HR",
    "nl_BE",
    "en_GB",
    "et_EE",
    "fo_FO",
    "fr_CA",
    "ka_GE",
    "el_GR",
    "gu_IN",
    "hi_IN",
    "is_IS",
    "id_ID",
    "ga_IE",
    "jv_ID",
    "kn_IN",
    "kk_KZ",
    "lv_LV",
    "lt_LT",
    "mk_MK",
    "mg_MG",
    "ms_MY",
    "mt_MT",
    "mr_IN",
    "mn_MN",
    "ne_NP",
    "pa_IN",
    "sr_RS",
    "so_SO",
    "sw_KE",
    "tl_PH",
    "ta_IN",
    "te_IN",
    "ml_IN",
    "uk_UA",
    "uz_UZ",
    "vi_VN",
    "km_KH",
    "tg_TJ",
    "ar_AR",
    "he_IL",
    "ur_PK",
    "fa_IR",
    "ps_AF",
    "my_MM",
    "qz_MM",
    "or_IN",
    "si_LK",
    "rw_RW",
    "cb_IQ",
    "ha_NG",
    "ja_KS",
    "br_FR",
    "tz_MA",
    "co_FR",
    "as_IN",
    "ff_NG",
    "sc_IT",
    "sz_PL",
]


class LocalizedObj:
    def __init__(self, locale, obj):
        if locale not in SUPPORTED_LOCALES:
            raise ValueError("Unsupported locale: {}".format(locale))
        if not obj:
            raise ValueError("Object is mandatory")
        self.locale = locale
        self.obj = obj





class SenderAction:
    TYPING_ON = 'typing_on'
    TYPING_OFF = 'typing_off'
    MARK_SEEN = 'mark_seen'


# def event_parser(messaging=None):
#     if messaging is None:
#         messaging = dict()
#
#     if 'message' in messaging:
#         is_echo = messaging.get('message', {}).get('is_echo')
#         if is_echo:
#             event_type = EchoEvent
#         else:
#             event_type = MessageEvent
#     elif 'delivery' in messaging:
#         event_type = DeliveriesEvent
#     elif 'read' in messaging:
#         event_type = ReadEvent.new_from_json_dict(messaging)
#     elif 'account_linking' in messaging:
#         event_type = AccountLinkingEvent
#     elif 'checkout_update' in messaging:
#         event_type = CheckOutUpdateEvent
#     elif 'game_play' in messaging:
#         event_type = GamePlayEvent.new_from_json_dict(messaging)
#     elif 'pass_thread_control' in messaging:
#         event_type = PassThreadEvent
#     elif 'take_thread_control' in messaging:
#         event_type = TakeThreadEvent
#     elif 'request_thread_control' in messaging:
#         event_type = RequestThreadEvent
#     elif 'app_roles' in messaging:
#         event_type = AppRoleEvent
#     elif 'optin' in messaging:
#         event_type = OptinEvent
#     elif 'payment' in messaging:
#         event_type = PaymentEvent
#     elif 'policy-enforcement' in messaging:
#         # key name must be changed for properly use to class instance.
#         messaging['policy_enforcement'] = messaging['policy-enforcement']
#         del messaging['policy-enforcement']
#         event_type = PolicyEnforcementEvent
#     elif 'postback' in messaging:
#         event_type = PostBackEvent
#     elif 'referral' in messaging:
#         event_type = ReferralEvent
#     elif 'standby' in messaging:
#         event_type = StandByEvent
#     else:
#         print("Webhook received unknown messaging")
#         return
#     event = event_type.new_from_json_dict(messaging)
#
#     return event



class Page:
    access_token: str
    verify_token: Optional[str] = None
    app_secret: Optional[str] = None
    api_version: str = 'v7.0'

    page: Optional[Me] = None

    def __init__(self, *,
                 auto_mark_as_seen: bool=True,
                 access_token: Optional[str] = None,
                 verify_token: Optional[str] = None,
                 app_secret: Optional[str] = None
                 ):
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


        # self._after_send = options.pop('after_send', None)
        # self._api_ver = options.pop('api_ver', 'v7.0')
        # if self._api_ver not in SUPPORTED_API_VERS:
        #     raise ValueError('Unsupported API Version : ' + self._api_ver)


    _entryCaster = {
        MessageEntry: MessageEvent,
        PostbacksEntry: PostBackEvent
    }

    # these are set by decorators or the 'set_webhook_handler' method
    _webhook_handlers = {}
    _webhook_handlers_sync = {}

    _quick_reply_callbacks = {}
    _button_callbacks = {}

    _quick_reply_callbacks_key_regex = {}
    _button_callbacks_key_regex = {}

    _after_send = None

    @property
    def base_api_furl(self) -> furl:
        furl_url = furl("https://graph.facebook.com/") / self.api_version
        # furl_url.args['access_token'] = self.access_token
        return furl_url

    def _api_uri(self, sub):
        return "https://graph.facebook.com/" + self.api_version + "/" + sub


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
            handler = self._webhook_handlers.get(type(entry))
            EntryConstructor = self._entryCaster.get(type(entry))
            if handler:
                await handler(EntryConstructor(entry))
            else:
                logger.warning("there's no {} handler", type(entry.theMessaging))

    @property
    def id(self):
        if self.page is None:
            self._fetch_page_info()

        return self.page.id

    @property
    def name(self):
        if self.page is None:
            self._fetch_page_info()

        return self.page.name

    def _fetch_page_info(self):
        r = requests.get(self.base_api_furl / "me",
                         params={"access_token": self.access_token},
                         headers={'Content-type': 'application/json'})

        if r.status_code != requests.codes.ok:
            print(r.text)
            return

        self.page = Me.parse_raw(r.text)

    def get_user_profile(self, fb_user_id) -> UserProfile:
        r = requests.get(self.base_api_furl / fb_user_id,
                         params={"access_token": self.access_token},
                         headers={'Content-type': 'application/json'})

        if r.status_code != requests.codes.ok:
            raise ConnectionError(r.text)

        user_profile = UserProfile.parse_raw(r.text)
        return user_profile

    def get_messenger_code(self, ref=None, image_size=1000):
        d = {}
        d['type']='standard'
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

    def _send(self, payload, callback=None) -> SendResponse:
        response = requests.post(self._api_uri("me/messages"),
                          params={"access_token": self.access_token},
                          data=payload.to_json(),
                          headers={'Content-type': 'application/json'})

        if response.status_code != requests.codes.ok:
            print(response.text)

        if callback is not None:
            callback(payload, response)

        if self._after_send is not None:
            self._after_send(payload, response)

        return SendResponse.parse_raw(response.text)

    def send(self, recipient_id, message, *, quick_replies=None, metadata=None,
             notification_type=None, tag:Optional[MessageTag]=None, callback: Optional[callable]=None):

        if self.auto_mark_as_seen:
            self.mark_seen(recipient_id)

        text = message if isinstance(message, str) else None
        

        attachment = message if not text else None

        payload = Payload(recipient=Recipient(id=recipient_id),
                          message=Message(text=text,
                                          attachment=attachment,
                                          quick_replies=quick_replies,
                                          metadata=metadata),
                          notification_type=notification_type,
                          tag=tag)

        return self._send(payload, callback=callback)

    def send_json(self, json_payload, callback=None):
        return self._send(Payload(**json.loads(json_payload)), callback)

    def send_dict(self, dict_payload, callback=None):
        return self._send(Payload(**dict_payload), callback)

    def typing_on(self, recipient_id):
        payload = Payload(recipient=Recipient(id=recipient_id),
                          sender_action=SenderAction.TYPING_ON)

        self._send(payload)

    def typing_off(self, recipient_id):
        payload = Payload(recipient=Recipient(id=recipient_id),
                          sender_action=SenderAction.TYPING_OFF)

        self._send(payload)

    def mark_seen(self, recipient_id):
        payload = Payload(recipient=Recipient(id=recipient_id),
                          sender_action=SenderAction.MARK_SEEN)

        self._send(payload)

    """
    messenger profile (see https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api)
    """

    def _set_profile_property(self, pname, pval):
        r = requests.post(self._api_uri("me/messenger_profile"),
                          params={"access_token": self.access_token},
                          data=json.dumps({
                              pname: pval
                          }),
                          headers={'Content-type': 'application/json'})

        if r.status_code != requests.codes.ok:
            print(r.text)

    def _del_profile_property(self, pname):
        r = requests.delete(self._api_uri("me/messenger_profile"),
                            params={"access_token": self.access_token},
                            data=json.dumps({
                                'fields': [pname,]
                            }),
                            headers={'Content-type': 'application/json'})

        if r.status_code != requests.codes.ok:
            print(r.text)

    def greeting(self, text):
        self.localized_greeting([LocalizedObj(locale="default", obj=text)])

    def localized_greeting(self, locale_list):
        if not locale_list:
            raise ValueError("List of locales is mandatory")
        pval = []
        for l in locale_list:
            if not isinstance(l, LocalizedObj):
                raise ValueError("greeting type error")
            if not isinstance(l.obj, str):
                raise ValueError("greeting text error")
            pval.append({
                "locale": l.locale,
                "text": l.obj
            })
        self._set_profile_property(pname="greeting", pval=pval)

    def hide_greeting(self):
        self._del_profile_property(pname="greeting")

    def show_starting_button(self, payload):
        if not payload or not isinstance(payload, str):
            raise ValueError("show_starting_button payload error")
        self._set_profile_property(pname="get_started",
                                   pval={"payload": payload})

    def hide_starting_button(self):
        self._del_profile_property(pname="get_started")

    def show_persistent_menu(self, buttons: Buttons) -> None:
        self.show_localized_persistent_menu([LocalizedObj(locale="default",
                                                          obj=buttons)])
    def hide_persistent_menu(self):
        self._del_profile_property(pname="persistent_menu")

    def show_localized_persistent_menu(self, locale_list):
        if not locale_list:
            raise ValueError("List of locales is mandatory")
        pval = []
        for l in locale_list:
            if not isinstance(l, LocalizedObj):
                raise ValueError("persistent_menu error")
            if not isinstance(l.obj, list):
                raise ValueError("menu call_to_actions error")

            buttons = Buttons.convert_shortcut_buttons(l.obj)

            buttons_dict = []
            for button in buttons:
                if isinstance(button, ButtonWeb):
                    buttons_dict.append({
                        "type": "web_url",
                        "title": button.title,
                        "url": button.url
                    })
                elif isinstance(button, ButtonPostBack):
                    buttons_dict.append({
                        "type": "postback",
                        "title": button.title,
                        "payload": button.payload
                    })
                else:
                    raise ValueError('show_persistent_menu button type must be "url" or "postback"')

            pval.append({
                "locale": l.locale,
                "call_to_actions": buttons_dict
            })
        self._set_profile_property(pname="persistent_menu", pval=pval)



    """
    handlers and decorations
    """
    def set_webhook_handler(self, scope, callback):
        """
        Allows adding a webhook_handler as an alternative to the decorators
        """
        scope = scope.lower()

        if scope == 'after_send':
            self._after_send = callback
            return

        if scope not in Page.WEBHOOK_ENDPOINTS:
            raise ValueError("The 'scope' argument must be one of {}.".format(Page.WEBHOOK_ENDPOINTS))

        self._webhook_handlers[scope] = callback

    def handle_optin(self, func):
        self._webhook_handlers['optin'] = func

    def handle_message_sync(self, func: callable):
        self._webhook_handlers_sync[MessageEntry] = func

    def handle_message(self, func: callable):
        self._webhook_handlers[MessageEntry] = func

    def handle_echo(self, func):
        self._webhook_handlers['echo'] = func

    def handle_delivery(self, func):
        self._webhook_handlers['delivery'] = func

    def handle_postback_sync(self, func):
        self._webhook_handlers_sync[PostbacksEntry] = func

    def handle_postback(self, func):
        self._webhook_handlers[PostbacksEntry] = func

    def handle_read(self, func):
        self._webhook_handlers['read'] = func

    def handle_account_linking(self, func):
        self._webhook_handlers['account_linking'] = func

    def handle_referral(self, func):
        self._webhook_handlers['referral'] = func

    def handle_game_play(self, func):
        self._webhook_handlers['game_play'] = func

    def handle_pass_thread_control(self, func):
        self._webhook_handlers['pass_thread_control'] = func

    def handle_take_thread_control(self, func):
        self._webhook_handlers['take_thread_control'] = func

    def handle_request_thread_control(self, func):
        self._webhook_handlers['request_thread_control'] = func

    def handle_app_roles(self, func):
        self._webhook_handlers['app_roles'] = func

    def handle_policy_enforcement(self, func):
        self._webhook_handlers['policy_enforcement'] = func

    def handle_checkout_update(self, func):
        self._webhook_handlers['checkout_update'] = func

    def handle_payment(self, func):
        self._webhook_handlers['payment'] = func

    def handle_standby(self, func):
        self._webhook_handlers['standby'] = func


    def after_send(self, func):
        self._after_send = func

    _callback_default_types = ['QUICK_REPLY', 'POSTBACK']

    def callback(self, payloads=None, types=None):
        if types is None:
            types = self._callback_default_types

        if not isinstance(types, list):
            raise ValueError('callback types must be list')

        for type in types:
            if type not in self._callback_default_types:
                raise ValueError('callback types must be "QUICK_REPLY" or "POSTBACK"')

        def wrapper(func):
            if payloads is None:
                return func

            for payload in payloads:
                if 'QUICK_REPLY' in types:
                    self._quick_reply_callbacks[payload] = func
                if 'POSTBACK' in types:
                    self._button_callbacks[payload] = func

            return func

        return wrapper

    def get_quick_reply_callbacks(self, event):
        callbacks = []
        for key in self._quick_reply_callbacks.keys():
            if key not in self._quick_reply_callbacks_key_regex:
                self._quick_reply_callbacks_key_regex[key] = re.compile(key + '$')

            if self._quick_reply_callbacks_key_regex[key].match(event.quick_reply_payload):
                callbacks.append(self._quick_reply_callbacks[key])

        return callbacks

    def get_postback_callbacks(self, event):
        callbacks = []
        for key in self._button_callbacks.keys():
            if key not in self._button_callbacks_key_regex:
                self._button_callbacks_key_regex[key] = re.compile(key + '$')

            if self._button_callbacks_key_regex[key].match(event.payload):
                callbacks.append(self._button_callbacks[key])

        return callbacks
