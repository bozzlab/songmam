import importlib
import re
from asyncio import coroutine
from inspect import iscoroutine
from itertools import product
from typing import get_args

from path import Path
from typing import Optional, Union, List, Awaitable, Callable

from fastapi import FastAPI, Request
from loguru import logger
from parse import parse
from pydantic import ValidationError

from songmam.middleware import VerifyTokenMiddleware, AppSecretMiddleware
from songmam.models.webhook.events.messages import MessagesEvent
from songmam.models.webhook.events.postback import PostbackEvent
from songmam.models.webhook import Webhook


class WebhookHandler:
    verify_token: Optional[str] = None
    app_secret: Optional[str] = None
    uncaught_postback_handler: Optional[Callable]= None

    def __init__(self, app: FastAPI, path="/", *, app_secret: Optional[str] = None, dynamic_import=True,
                 verify_token: Optional[str] = None, auto_mark_as_seen: bool = True):
        self._post_webhook_handlers = {}
        self._pre_webhook_handlers = {}
        self.app = app
        self.verify_token = verify_token
        self.app_secret = app_secret
        self.path = path
        self.dynamic_import = dynamic_import


        app.add_middleware(VerifyTokenMiddleware, verify_token=verify_token, path=path)
        if not self.verify_token:
            logger.warning(
                "Without verify token, It is possible for your bot server to be substituded by hackers' server.")

        if self.app_secret:
            app.add_middleware(AppSecretMiddleware, app_secret=app_secret, path=path)
        else:
            logger.warning("Without app secret, The server will not be able to identity the integrety of callback.")

        @app.post(path)
        async def handle_entry(request: Request):
            body = await request.body()
            try:
                webhook = Webhook.parse_raw(body)
            except ValidationError as e:
                logger.error("Cannot validate webhook")
                logger.error("Body is {}", body)
                raise e
            await self.handle_webhook(webhook)
            return "ok"



    # these are set by decorators or the 'set_webhook_handler' method
    _webhook_handlers = {}

    _quick_reply_callbacks = {}
    _button_callbacks = {}
    _delivered_callbacks = {}

    _quick_reply_callbacks_key_regex = {}
    _button_callbacks_key_regex = {}
    _delivered_callbacks_key_regex = {}

    async def handle_webhook(self, webhook: Webhook, *args, **kwargs):
        for entry in webhook.entry:
            entry_type = type(entry)

            # Unconditional handlers
            handler = self._webhook_handlers.get(entry_type)
            if handler:
                await handler(entry, *args, **kwargs)
            else:
                if not self.dynamic_import and entry_type is PostbackEvent:
                    logger.warning("there's no handler for this entry type, {}", str(entry_type))

            # Dynamic handlers
            if entry_type is MessagesEvent:
                if entry.is_quick_reply:
                    if self.dynamic_import:
                        await self.call_dynamic_function(entry, *args, **kwargs)
                        continue
                    else:
                        matched_callbacks = self.get_quick_reply_callbacks(entry)
                        for callback in matched_callbacks:
                            await callback(entry, *args, **kwargs)
            elif entry_type is PostbackEvent:
                if self.dynamic_import:
                    await self.call_dynamic_function(entry, *args, **kwargs)
                    continue
                matched_callbacks = self.get_postback_callbacks(entry)
                for callback in matched_callbacks:
                    await callback(entry, *args, **kwargs)


    async def call_dynamic_function(self, entry: Union[MessagesEvent, PostbackEvent], *args, **kwargs):
        payload = entry.payload
        parsed = parse("{import_path}:{function_name}", payload)
        import_path = parsed['import_path']
        function_name = parsed['function_name']

        try:
            module = importlib.import_module(f"{import_path}")
            function = getattr(module, function_name)
            ret = function(entry, *args, **kwargs)
            if iscoroutine(ret):
                await ret
        except ModuleNotFoundError as e:
            if self.uncaught_postback_handler:
                ret = self.uncaught_postback_handler(entry, *args, **kwargs)
                if iscoroutine(ret):
                    await ret
            else:
                logger.warning("Please add `uncaught_postback_handler` to caught this '{}' payload", entry.payload)

    def add_pre(self, entry_type):
        """
        Add an unconditional event handler
        """

        def decorator(func):
            self._pre_webhook_handlers[entry_type] = func
            # if isinstance(text, (list, tuple)):
            #     for it in text:
            #         self.__add_handler(func, entry, text=it)
            # else:
            #     self.__add_handler(func, entry, text=text)

            return func

        return decorator

    def add(self, event_type,
            # skipQuickReply:Optional[bool]=None
            ):
        """
        Add an event handler
        """
        # conditions = tuple(skipQuickReply)
        # didPassSomeCondition = any((x is None for x in conditions))
        # spaces = [(event_type), ]
        # for con in conditions:
        #     if get_args(con) is bool:
        #         if con is None:
        #             spaces.append((True, False))
        #         else:
        #             spaces.append(tuple(con))



        def decorator(func):
            # for condition in product(*spaces):
            self._webhook_handlers[event_type] = func

            # if isinstance(text, (list, tuple)):
            #     for it in text:
            #         self.__add_handler(func, entry, text=it)
            # else:
            #     self.__add_handler(func, entry, text=text)

            return func

        return decorator

    def add_post(self, entry_type):
        """
        Add an unconditional post event handler
        """

        def decorator(func):
            self._post_webhook_handlers[entry_type] = func
            # if isinstance(text, (list, tuple)):
            #     for it in text:
            #         self.__add_handler(func, entry, text=it)
            # else:
            #     self.__add_handler(func, entry, text=text)

            return func

        return decorator

    def add_postback_handler(self, regexes: List[str] = None, quick_reply=True, button=True):

        def wrapper(func):
            if regexes is None:
                return func

            for payload in regexes:
                if quick_reply:
                    self._quick_reply_callbacks[payload] = func
                if button:
                    self._button_callbacks[payload] = func

            return func

        return wrapper

    def set_uncaught_postback_handler(self, func):
        self.uncaught_postback_handler = func
        return func

    def get_quick_reply_callbacks(self, entry: MessagesEvent):
        callbacks = []
        for key in self._quick_reply_callbacks.keys():
            if key not in self._quick_reply_callbacks_key_regex:
                self._quick_reply_callbacks_key_regex[key] = re.compile(key + '$')

            if self._quick_reply_callbacks_key_regex[key].match(entry.payload):
                callbacks.append(self._quick_reply_callbacks[key])

        return callbacks

    def get_postback_callbacks(self, entry: PostbackEvent):
        callbacks = []
        for key in self._button_callbacks.keys():
            if key not in self._button_callbacks_key_regex:
                self._button_callbacks_key_regex[key] = re.compile(key + '$')

            if self._button_callbacks_key_regex[key].match(entry.payload):
                callbacks.append(self._button_callbacks[key])

        return callbacks
