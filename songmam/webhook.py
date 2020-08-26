from typing import Optional

from fastapi import FastAPI
from loguru import logger

from songmam.middleware import VerifyTokenMiddleware, AppSecretMiddleware


class WebhookHandler:
    verify_token: Optional[str] = None
    app_secret: Optional[str] = None

    def __init__(self,app: FastAPI, app_secret: Optional[str] = None, verify_token: Optional[str] = None, *, auto_mark_as_seen: bool = True):
        self.app = app
        self.verify_token = verify_token
        self.app_secret = app_secret

        if self.verify_token:
            app.add_middleware(VerifyTokenMiddleware, verify_token=verify_token)
        else:
            logger.warning("Without verify token, It is possible for your bot server to be substituded by hackers' server.")
        if self.app_secret:
            app.add_middleware(AppSecretMiddleware, app_secret=app_secret)
        else:
            logger.warning("Without app secret, The server will not be able to identity the integrety of callback.")


    # these are set by decorators or the 'set_webhook_handler' method
    _webhook_handlers = {}

    _quick_reply_callbacks = {}
    _button_callbacks = {}
    _delivered_callbacks = {}

    _quick_reply_callbacks_key_regex = {}
    _button_callbacks_key_regex = {}
    _delivered_callbacks_key_regex = {}

    _after_send = None


    async def handle_webhook(self, webhook: Webhook, request: Request):

        for entry in webhook.entry:
            entry_type = type(entry)
            handler = self._webhook_handlers.get(entry_type)
            eventConstructor = self._entryCaster.get(entry_type)
            if handler:
                event = eventConstructor(entry)

                if entry_type is MessageEntry:
                    if self.auto_mark_as_seen:
                        await self.mark_seen(event.sender)

                    if event.is_quick_reply:
                        matched_callbacks = self.get_quick_reply_callbacks(event)
                        for callback in matched_callbacks:
                            await callback(event, request)

                elif entry_type is PostbackEntry:
                    matched_callbacks = self.get_postback_callbacks(event)
                    for callback in matched_callbacks:
                        await callback(event, request)
                elif entry_type is ReferralEntry:
                    pass

                elif entry_type is DeliveriesEntry:
                    pass

                await handler(event, request)
            else:
                logger.warning("there's no handler for entry type", entry_type)

    """
    handlers and decorations
    """

    def set_webhook_handler(self, entry_type, callback):
        """
        Allows adding a webhook_handler as an alternative to the decorators
        """
        # scope = scope.lower()
        #
        # if scope == 'after_send':
        #     self._after_send = callback
        #     return

        self._webhook_handlers[entry_type] = callback

    def add(self, callback, *, entry_type):
        """
        Allows adding a webhook_handler as an alternative to the decorators
        """

        self._webhook_handlers[entry_type] = callback

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
