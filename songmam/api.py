import httpx
from furl import furl


class MessengerApi:
    access_token: str
    api_version: str = 'v7.0'

    @property
    def base_api_furl(self) -> furl:
        furl_url = furl("https://graph.facebook.com/") / self.api_version
        # furl_url.args['access_token'] = self.access_token
        return furl_url

    async def _fetch_page_info(self):
        async with httpx.AsyncClient(base_url=self.base_api_furl.url, headers={'Content-type': 'application/json'},
                                     params={"access_token": self.access_token}) as client:
            response = await client.get(
                f"/me"
            )

        if response.status_code != 200:
            raise Exception(response.text)

        self.page = Me.parse_raw(response.text)


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
            raise Exception(r.text)

        data = json.loads(r.text)
        if 'uri' not in data:
            raise ValueError('Could not fetch messener code : GET /' +
                             self.api_version + '/me')

        return data['uri']


    async def send_native(self, payload: Union[CompletePayload], callback=None) -> SendResponse:

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
            callback_output = callback(payload, response)
            if callback_output is Awaitable:
                await callback

        if self._after_send is not None:
            return_ = self._after_send(payload, response)
            if return_ is Awaitable:
                await return_

        return SendResponse.parse_raw(response.text)

    async def send_receipt(self):
        from dataclasses import dataclass
        from typing import Optional, List

        from songmam.models.messaging.quick_replies import QuickReply
        from songmam.models.messaging.templates import TemplateAttachment, Message
        from songmam.models.messaging.templates.receipt import ReceiptElements, Address, Summary, Adjustments, \
            PayloadReceipt

        @dataclass
        class ContentReceipt:
            quick_replies: Optional[List[QuickReply]]
            sharable: Optional[bool]
            recipient_name: str
            merchant_name: Optional[str]
            order_number: str
            currency: str
            payment_method: str  # This can be a custom string, such as, "Visa 1234".
            timestamp: Optional[str]
            elements: Optional[List[ReceiptElements]]
            address: Optional[Address]
            summary: Summary
            adjustments: Optional[List[Adjustments]]

            @property
            def message(self):
                message = Message()

                if self.elements:
                    payload = PayloadReceipt(
                        template_type="receipt",
                        recipient_name=self.recipient_name,
                        order_number=self.order_number,
                        currency=self.currency,
                        payment_method=self.payment_method,  # This can be a custom string, such as, "Visa 1234".
                        summary=self.summary,
                    )
                    payload.sharable = self.sharable
                    payload.merchant_name = self.merchant_name
                    payload.timestamp = self.timestamp
                    payload.elements = self.elements
                    payload.address = self.address
                    payload.adjustments = self.adjustments
                    message.attachment = TemplateAttachment(
                        payload=payload
                    )
                if self.quick_replies:
                    message.quick_replies = self.quick_replies

                return message

        raise NotImplementedError

    async def send_media(self):
        raise NotImplementedError

    async def send_generic(self):
        raise NotImplementedError

    async def send(self,
                   recipient: Union[Sender, str],
                   message: Optional[str] = None,
                   *,
                   buttons: Optional[Union[AllButtonTypes, List[AllButtonTypes]]] = None,
                   quick_replies: Optional[List[QuickReply]] = None,
                   generic_elements: Optional[Union[GenericElement, List[GenericElement]]] = None,
                   image_aspect_ratio: Optional[Literal["horizontal", "square"]] = None,
                   media_element: Optional[MediaElement] = None,
                   media_sharable: Optional[bool] = None,
                   persona_id: Optional[str] = None,
                   messaging_type: Optional[MessagingType] = MessagingType.RESPONSE,
                   tag: Optional[MessageTag] = None,
                   notification_type: Optional[NotificationType] = NotificationType.REGULAR,
                   callback: Optional[callable] = None,
                   emu_type: bool = False
                   ):
        # auto cast
        if isinstance(recipient, str):
            recipient = Sender(id=recipient)

        if message:
            typing_fn = partial(self.typing_on, recipient)
            stop_fn = partial(self.typing_off, recipient)
            if emu_type:
                await self.bubbling.act_typing(message, typing_fn, stop_fn)
            else:
                if self.emu_type:
                    await self.bubbling.act_typing(message, typing_fn, stop_fn)

        # auto cast 2
        if buttons:
            if not isinstance(buttons, list):
                buttons = [buttons]

            payload = CompletePayload(
                recipient=recipient,
                message=Message(
                    attachment=TemplateAttachment(
                        payload=PayloadButtonTemplate(
                            template_type='button',
                            text=message,
                            buttons=buttons
                        )
                    ),
                    quick_replies=quick_replies
                ),
                persona_id=persona_id,
                messaging_type=messaging_type,
                tag=tag,
                notification_type=notification_type,
            )
        elif generic_elements:
            if not isinstance(generic_elements, list):
                generic_elements = [generic_elements]

            payload = CompletePayload(
                recipient=recipient,
                message=Message(
                    attachment=TemplateAttachment(
                        payload=PayloadGeneric(
                            elements=generic_elements,
                            image_aspect_ratio=image_aspect_ratio
                        )
                    ),
                    quick_replies=quick_replies
                ),
                persona_id=persona_id,
                messaging_type=messaging_type,
                tag=tag,
                notification_type=notification_type,
            )
        elif media_element:
            payload = CompletePayload(
                recipient=recipient,
                message=Message(
                    attachment=TemplateAttachment(
                        payload=PayloadMedia(
                            elements=[media_element],
                            sharable=media_sharable,
                        )
                    ),
                    quick_replies=quick_replies
                ),
                persona_id=persona_id,
                messaging_type=messaging_type,
                tag=tag,
                notification_type=notification_type,
            )
        else:
            payload = CompletePayload(
                recipient=recipient,
                message=Message(
                    text=message,
                    quick_replies=quick_replies
                ),
                persona_id=persona_id,
                messaging_type=messaging_type,
                tag=tag,
                notification_type=notification_type,
            )

        return await self.send_native(payload, callback=callback)

    # def reply_sync(self, message_to_reply_to: MessageEvent, message: ContentButton, *, quick_replies=None,
    #                metadata=None,
    #                notification_type=None, tag: Optional[MessageTag] = None, callback: Optional[callable] = None):
    #
    #     if self.prevent_repeated_reply:
    #         message_id = message_to_reply_to.entry.theMessaging.message.mid
    #         if message_id not in self.reply_cache:
    #             # good to go
    #             self.reply_cache.set(message_id, True)
    #         else:
    #             logger.warning("Songmum prevented a message from being reply to the same event multiple times.")
    #             logger.warning(message_to_reply_to)
    #             return
    #
    #     return self.send_native_sync(
    #         CompletePayload(
    #             recipient=message_to_reply_to.sender,
    #             message=message.message
    #         ), callback_sync=callback)
    #
    # async def reply(self, message_to_reply_to: MessageEvent, message, *, quick_replies=None, metadata=None,
    #                 notification_type=None, tag: Optional[MessageTag] = None, callback: Optional[callable] = None):
    #
    #     if self.prevent_repeated_reply:
    #         message_id = message_to_reply_to.entry.theMessaging.message.mid
    #         if message_id not in self.reply_cache:
    #             # good to go
    #             self.reply_cache.set(message_id, True)
    #         else:
    #             logger.warning("Songmum prevented a message from being reply to the same event multiple times.")
    #             logger.warning(message_to_reply_to)
    #             return
    #
    #     return await self.send_native(
    #         CompletePayload(
    #             recipient=message_to_reply_to.sender,
    #             message=message.message
    #         ),
    #         callback=callback
    #     )

    async def typing_on(self, recipient: Type[ThingWithId]):
        payload = SenderActionPayload(recipient=recipient,
                                      sender_action=SenderAction.TYPING_ON)

        return await self.send(payload)

    async def typing_off(self, recipient: Type[ThingWithId]):
        payload = SenderActionPayload(recipient=recipient,
                                      sender_action=SenderAction.TYPING_OFF)

        return await self.send_native(payload)

    async def mark_seen(self, recipient: Type[ThingWithId]):
        payload = SenderActionPayload(recipient=recipient,
                                      sender_action=SenderAction.MARK_SEEN)

        return await self.send_native(payload)

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

    def set_user_menu(self, user: Union[str, Type[ThingWithId]], menus: List[MenuPerLocale]):
        if isinstance(user, str):
            user = ThingWithId(id=user)

        if isinstance(menus, MenuPerLocale):
            menus = [menus]

        f_url = self.base_api_furl / 'me' / 'custom_user_settings'
        r = requests.post(f_url.url,
                          params={"access_token": self.access_token},
                          data=UserPersistentMenu(
                              psid=user.id,
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

    async def create_persona(self, persona: Persona) -> PersonaResponse:
        data = persona.json()

        async with httpx.AsyncClient(base_url=self.base_api_furl.url, headers={'Content-type': 'application/json'},
                                     params={"access_token": self.access_token}) as client:
            response = await client.post(
                "/me/personas",
                data=data,
            )

        if response.status_code != 200:
            raise Exception(response.text)

        return PersonaResponse.parse_raw(response.text)

    async def get_persona(self, id):

        async with httpx.AsyncClient(base_url=self.base_api_furl.url, headers={'Content-type': 'application/json'},
                                     params={"access_token": self.access_token}) as client:
            response = await client.get(
                f"/{id}",
            )

        if response.status_code != 200:
            raise Exception(response.text)

        return PersonaWithId.parse_raw(response.text)

    async def get_all_personas(self) -> List[PersonaWithId]:

        async with httpx.AsyncClient(base_url=self.base_api_furl.url, headers={'Content-type': 'application/json'},
                                     params={"access_token": self.access_token}) as client:
            response = await client.get(
                f"/me/personas",
            )

        if response.status_code != 200:
            raise Exception(response.text)

        response = AllPerosnasResponse.parse_raw(response.text)

        # There might be a need to implement paging in future
        # Note: https://developers.facebook.com/docs/graph-api/using-graph-api/#cursors

        return response.data

    async def delete_persona(self, id):

        async with httpx.AsyncClient(base_url=self.base_api_furl.url, headers={'Content-type': 'application/json'},
                                     params={"access_token": self.access_token}) as client:
            response = await client.delete(
                f"/{id}",
            )

        if response.status_code != 200:
            raise Exception(response.text)

        return PersonaDeleteResponse.parse_raw(response.text)