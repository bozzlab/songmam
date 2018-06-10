import unittest
import json
import mock
import responses
from fbmq.fbmq import Page, LocalizedObj, SUPPORTED_API_VERS
from fbmq import template as Template
from fbmq import events as Event


class MessengerAPIMock():
    GET = responses.GET
    PUT = responses.PUT
    POST = responses.POST
    DELETE = responses.DELETE
    METHODS = [responses.GET, responses.PUT, responses.POST, responses.DELETE]

    def __init__(self, subpath, expected=None, method=None, utest=None,
                 api_ver=None):
        self.subpath = subpath
        self.expected = None
        self.method = method if method else self.POST
        self.utest = utest
        self.set_expected(expected=expected)
        self.req_mock = responses.RequestsMock()
        self.api_ver = api_ver if api_ver else 'v2.6'

    def __enter__(self):
        self.req_mock.start()
        self.req_mock.add(method=self.method,
                          url="https://graph.facebook.com/" + self.api_ver +
                              "/me/" + self.subpath)
        return self

    def __exit__(self, type, value, traceback):
        if self.utest:
            self.utest.assertEqual(self.nof_requests, 1,
                                   "Invalid number of requests: {}".format(
                                       self.nof_requests))
            if self.expected:
                self.utest.assertEqual(json.loads(self.req(0).body),
                                       self.expected,
                                       "Expectation Failed")
        self.req_mock.stop(allow_assert=False)
        self.req_mock.reset()

    def set_expected(self, expected):
        if not expected:
            self.expected = None
        elif isinstance(expected, str):
            self.expected = json.loads(expected)
        elif isinstance(expected, dict):
            self.expected = expected
        else:
            assert "Bad expected type"

    def req(self, idx):
        return self.req_mock.calls[idx].request if idx < self.nof_requests \
            else None

    @property
    def nof_requests(self):
        return len(self.req_mock.calls)

    @property
    def as_expected(self):
        return self.last_req and self.last_req.parsed_body == self.expected


class PageApiVerTest(unittest.TestCase):
    def test_supported_versions(self):
        for v in SUPPORTED_API_VERS:
            with MessengerAPIMock(subpath="messages", utest=self, api_ver=v)\
                    as m:
                Page('TOKEN', api_ver=v).send(12345, "hello world")

    def test_unsupported_version(self):
        with self.assertRaises(ValueError):
            Page('TOKEN', api_ver='bad_ver')


class PageTest(unittest.TestCase):
    def setUp(self):
        self.page = Page('TOKEN')
        self.page._send = mock.MagicMock()
        self.page._fetch_page_info = mock.MagicMock()

    def test_send(self):
        self.page.send(12345, "hello world", quick_replies=[{'title': 'Yes', 'payload': 'YES'}], callback=1)
        self.page._send.assert_called_once_with('{"message": {"attachment": null, "metadata": null, '
                                                '"quick_replies": '
                                                '[{"content_type": "text", "payload": "YES", "title": "Yes"}], '
                                                '"text": "hello world"},'
                                                ' "notification_type": null, '
                                                '"recipient": {"id": 12345}, '
                                                '"sender_action": null, '
                                                '"tag": null}', callback=1)

    def test_typingon(self):
        self.page.typing_on(1004)
        self.page._send.assert_called_once_with('{"message": null, "notification_type": null, '
                                                '"recipient": {"id": 1004}, '
                                                '"sender_action": "typing_on", '
                                                '"tag": null}')

    def test_typingoff(self):
        self.page.typing_off(1004)
        self.page._send.assert_called_once_with('{"message": null, "notification_type": null, '
                                                '"recipient": {"id": 1004}, '
                                                '"sender_action": "typing_off", '
                                                '"tag": null}')

    def test_markseen(self):
        self.page.mark_seen(1004)
        self.page._send.assert_called_once_with('{"message": null, "notification_type": null, '
                                                '"recipient": {"id": 1004}, '
                                                '"sender_action": "mark_seen", '
                                                '"tag": null}')

    def test_tag(self):
        self.page.send(12345, "hello world", quick_replies=[{'title': 'Yes', 'payload': 'YES'}], tag="PAIRING_UPDATE", callback=1)
        self.page._send.assert_called_once_with('{"message": {"attachment": null, "metadata": null, '
                                                '"quick_replies": '
                                                '[{"content_type": "text", "payload": "YES", "title": "Yes"}], '
                                                '"text": "hello world"},'
                                                ' "notification_type": null, '
                                                '"recipient": {"id": 12345}, '
                                                '"sender_action": null, '
                                                '"tag": "PAIRING_UPDATE"}', callback=1)

    def test_handle_webhook_errors(self):
        payload = """
        {
            "object":"not_a_page",
            "entry":[
                {"id":"1691462197845448","time":1472026867114,
                "messaging":[
                    {"sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472026867080,
                     "message":{"mid":"mid.1472026867074:cfb5e1d4bde07a2a55","seq":812,"text":"hello world"}}
                ]}
            ]
        }
        """
        self.assertFalse(self.page.handle_webhook(payload))

        payload = """
        {
            "object":"page",
            "entry":[
                {"id":"1691462197845448","time":1472026867114,
                "messaging":[
                    {"sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472026867080,
                     "unknown":{"mid":"mid.1472026867074:cfb5e1d4bde07a2a55","seq":812,"text":"hello world"}}
                ]}
            ]
        }
        """

        self.page.handle_webhook(payload)

        @self.page.callback
        def unknown():
            pass

    def test_page_info(self):
        self.assertEquals(0, self.page._fetch_page_info.call_count)
        self.page.page_id
        self.assertEquals(1, self.page._fetch_page_info.call_count)
        self.page.page_name
        self.assertEquals(2, self.page._fetch_page_info.call_count)

        self.page._page_id = 1
        self.page._page_name = 'name'
        print(self.page.page_id, self.page.page_name)

        self.assertEquals(2, self.page._fetch_page_info.call_count)

    def test_set_webhook_handler(self):

        def dummy_func():
            pass

        with self.assertRaises(ValueError):
            self.page.set_webhook_handler("shouldfail", dummy_func)

        self.page.set_webhook_handler("message", dummy_func)
        self.assertEqual(self.page._webhook_handlers["message"], dummy_func)

        # clean up
        self.page._webhook_handlers["message"] = None

    def test_handle_webhook_message(self):
        payload = """
        {
            "object":"page",
            "entry":[
                {"id":"1691462197845448","time":1472026867114,
                "messaging":[
                    {"sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472026867080,
                     "message":{"mid":"mid.1472026867074:cfb5e1d4bde07a2a55","seq":812,"text":"hello world"}}
                ]}
            ]
        }
        """
        counter = mock.MagicMock()
        self.page.handle_webhook(payload)

        @self.page.handle_message
        def handler1(event):
            self.assertTrue(event, Event.MessageEvent)
            self.assertEqual(event.name, 'message')
            self.assertEqual(event.attachments, [])
            self.assertFalse(event.is_quick_reply)
            self.assertEquals(event.timestamp, 1472026867080)
            self.assertEquals(event.sender_id, '1134343043305865')
            self.assertEquals(event.recipient_id, '1691462197845448')
            self.assertEquals(event.text, 'hello world')
            counter()

        self.page.handle_webhook(payload)
        self.assertEquals(1, counter.call_count)

        counter2 = mock.MagicMock()

        def handler2(event):
            counter2()

        self.page.handle_webhook(payload, message=handler2)
        self.assertEquals(1, counter2.call_count)

    def test_handle_webhook_read(self):
        payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472026870339,
        "messaging":[{
            "sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472026869186,
            "read":{"watermark":1472026868763,"seq":814}}]
        }]}
        """
        counter = mock.MagicMock()

        @self.page.handle_read
        def handler1(event):
            self.assertTrue(isinstance(event, Event.ReadEvent))
            self.assertEqual(event.name, 'read')
            self.assertEqual(event.seq, 814)
            self.assertEqual(event.watermark, 1472026868763)
            self.assertEquals(event.timestamp, 1472026869186)
            self.assertEquals(event.sender_id, '1134343043305865')
            self.assertEquals(event.recipient_id, '1691462197845448')
            counter()

        self.page.handle_webhook(payload)
        self.assertEquals(1, counter.call_count)

        counter2 = mock.MagicMock()

        def handler2(event):
            counter2()

        self.page.handle_webhook(payload, read=handler2)
        self.assertEquals(1, counter2.call_count)

    def test_handle_webhook_echo(self):
        payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472026869143,
        "messaging":[{
            "sender":{"id":"1691462197845448"},"recipient":{"id":"1134343043305865"},"timestamp":1472026868763,
            "message":{"is_echo":true,"app_id":950864918368986,"mid":"mid.1472026868734:832ecbdfc1ffc30139","seq":813,
            "text":"hello"}}]
        }]}
        """
        counter = mock.MagicMock()

        @self.page.handle_echo
        def handler1(event):
            self.assertTrue(isinstance(event, Event.EchoEvent))
            self.assertEqual(event.name, 'echo')
            self.assertEqual(event.mid, "mid.1472026868734:832ecbdfc1ffc30139")
            self.assertEqual(event.app_id, 950864918368986)
            self.assertEqual(event.text, 'hello')
            self.assertEquals(event.timestamp, 1472026868763)
            self.assertEquals(event.sender_id, '1691462197845448')
            self.assertEquals(event.recipient_id, '1134343043305865')
            counter()

        self.page.handle_webhook(payload)
        self.assertEquals(1, counter.call_count)

        counter2 = mock.MagicMock()

        def handler2(event):
            counter2()

        self.page.handle_webhook(payload, echo=handler2)
        self.assertEquals(1, counter2.call_count)

    def test_handle_webhook_delivery(self):
        payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472028396029,
            "messaging":[{"sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":0,
            "delivery":{"mids":["mid.1472028395154:917e24ea99bc7d8f11"],"watermark":1472028395190,"seq":821}}
            ]}]}
        """
        counter = mock.MagicMock()

        @self.page.handle_delivery
        def handler1(event):
            self.assertTrue(isinstance(event, Event.DeliveriesEvent))
            self.assertEqual(event.name, 'delivery')
            self.assertEqual(event.mids, ["mid.1472028395154:917e24ea99bc7d8f11"])
            self.assertEqual(event.watermark, 1472028395190)
            self.assertEqual(event.seq, 821)
            self.assertEquals(event.timestamp, 0)
            self.assertEquals(event.sender_id, '1134343043305865')
            self.assertEquals(event.recipient_id, '1691462197845448')
            counter()

        self.page.handle_webhook(payload)
        self.assertEquals(1, counter.call_count)

        counter2 = mock.MagicMock()

        def handler2(event):
            counter2()

        self.page.handle_webhook(payload, delivery=handler2)
        self.assertEquals(1, counter2.call_count)

    def test_handle_webhook_account_linking(self):
        payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472028542079,
        "messaging":[{
            "sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472028542079,
            "account_linking":{"authorization_code":"1234567890","status":"linked"}}]}]}
        """
        counter = mock.MagicMock()

        @self.page.handle_account_linking
        def handler1(event):
            self.assertTrue(isinstance(event, Event.AccountLinkingEvent))
            self.assertEqual(event.name, 'account_linking')
            self.assertEqual(event.status, 'linked')
            self.assertTrue(event.is_linked)
            self.assertEqual(event.authorization_code, "1234567890")
            self.assertEquals(event.timestamp, 1472028542079)
            self.assertEquals(event.sender_id, '1134343043305865')
            self.assertEquals(event.recipient_id, '1691462197845448')
            counter()

        self.page.handle_webhook(payload)
        self.assertEquals(1, counter.call_count)

        counter2 = mock.MagicMock()

        def handler2(event):
            counter2()

        self.page.handle_webhook(payload, account_linking=handler2)
        self.assertEquals(1, counter2.call_count)

    def test_handle_webhook_referral(self):
        payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472028542079,
        "messaging":[{
            "sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472028542079,
            "referral":{"ref":"REFTEST","source":"SHORTLINK","type": "OPEN_THREAD"}}]}]}
        """
        counter = mock.MagicMock()

        @self.page.handle_referral
        def handler1(event):
            self.assertTrue(isinstance(event, Event.ReferralEvent))
            self.assertEqual(event.name, 'referral')
            self.assertEqual(event.source, 'SHORTLINK')
            self.assertEqual(event.type, 'OPEN_THREAD')
            self.assertEqual(event.ref, 'REFTEST')
            self.assertEqual(event.referer_uri, None)
            self.assertEquals(event.timestamp, 1472028542079)
            self.assertEquals(event.sender_id, '1134343043305865')
            self.assertEquals(event.recipient_id, '1691462197845448')
            counter()

        self.page.handle_webhook(payload)
        self.assertEquals(1, counter.call_count)

        counter2 = mock.MagicMock()

        def handler2(event):
            counter2()

        self.page.handle_webhook(payload, referral=handler2)
        self.assertEquals(1, counter2.call_count)

    def test_handle_webhook_postback(self):
        payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472028006107,
        "messaging":[{
            "sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472028006107,
            "postback":{"payload":"DEVELOPED_DEFINED_PAYLOAD"}}]
        }]}
        """
        counter1 = mock.MagicMock()

        @self.page.handle_postback
        def handler1(event):
            self.assertTrue(isinstance(event, Event.PostBackEvent))
            self.assertEqual(event.name, 'postback')
            self.assertEqual(event.title, None)
            self.assertEqual(event.payload, 'DEVELOPED_DEFINED_PAYLOAD')
            self.assertEquals(event.timestamp, 1472028006107)
            self.assertEquals(event.sender_id, '1134343043305865')
            self.assertEquals(event.recipient_id, '1691462197845448')
            counter1()

        self.page.handle_webhook(payload)
        self.assertEquals(1, counter1.call_count)

        counter2 = mock.MagicMock()

        def handler2(event):
            counter2()

        self.page.handle_webhook(payload, postback=handler2)
        self.assertEquals(1, counter2.call_count)

    def test_handle_webhook_postback_referral(self):
        payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472028006107,
        "messaging":[{
            "sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472028006107,
            "postback":{"payload":"DEVELOPED_DEFINED_PAYLOAD",
                        "referral":{"ref":"REFTEST","source":"SHORTLINK","type": "OPEN_THREAD"}}}]
        }]}
        """
        counter1 = mock.MagicMock()

        @self.page.handle_postback
        def handler1(event):
            self.assertTrue(isinstance(event, Event.PostBackEvent))
            self.assertEqual(event.name, 'postback')
            self.assertEquals(event.payload, 'DEVELOPED_DEFINED_PAYLOAD')
            self.assertEquals(event.referral, {"ref":"REFTEST","source":"SHORTLINK","type": "OPEN_THREAD"})
            self.assertEquals(event.timestamp, 1472028006107)
            self.assertEquals(event.sender_id, '1134343043305865')
            self.assertEquals(event.recipient_id, '1691462197845448')
            counter1()

        self.page.handle_webhook(payload)
        self.assertEquals(1, counter1.call_count)

        counter2 = mock.MagicMock()

        def handler2(event):
            counter2()

        self.page.handle_webhook(payload, postback=handler2)
        self.assertEquals(1, counter2.call_count)

    def test_handle_webhook_postback_button_callback(self):
        payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472028006107,
        "messaging":[{
            "sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472028006107,
            "postback":{"payload":"DEVELOPED_DEFINED_PAYLOAD"}}]
        }]}
        """
        counter1 = mock.MagicMock()
        counter2 = mock.MagicMock()

        def handler1(event):
            self.assertTrue(isinstance(event, Event.PostBackEvent))
            self.assertEquals(event.timestamp, 1472028006107)
            self.assertEquals(event.sender_id, '1134343043305865')
            self.assertEquals(event.recipient_id, '1691462197845448')
            counter1()

        @self.page.callback(['DEVELOPED_DEFINED_PAYLOAD'], types=['POSTBACK'])
        def button_callback(payload, event):
            counter2()

        self.page.handle_webhook(payload, postback=handler1)

        self.assertEquals(1, counter1.call_count)
        self.assertEquals(1, counter2.call_count)

        payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472028006107,
        "messaging":[{
            "sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472028006107,
            "postback":{"payload":"DEVELOPED_DEFINED_PAYLOAD2"}}]
        }]}
        """
        self.page.handle_webhook(payload, postback=handler1)
        self.assertEquals(2, counter1.call_count)
        self.assertEquals(1, counter2.call_count)

    def test_handle_webhook_quickreply_callback(self):
        payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472028637866,
        "messaging":[{
            "sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472028637825,
            "message":{"quick_reply":{"payload":"PICK_ACTION"},"mid":"mid.1472028637817:ae2763cc036a664b43","seq":834,"text":"Action"}}]}]}
        """
        counter1 = mock.MagicMock()
        counter2 = mock.MagicMock()

        @self.page.handle_message
        def handler1(event):
            self.assertTrue(isinstance(event, Event.MessageEvent))
            self.assertEqual(event.name, 'message')
            self.assertTrue(event.is_quick_reply)
            self.assertEquals(event.text, 'Action')
            self.assertEquals(event.timestamp, 1472028637825)
            self.assertEquals(event.sender_id, '1134343043305865')
            self.assertEquals(event.recipient_id, '1691462197845448')
            counter1()

        @self.page.callback(['PICK_ACTION'], types=['QUICK_REPLY'])
        def button_callback(payload, event):
            counter2()

        self.page.handle_webhook(payload, postback=handler1)

        self.assertEquals(1, counter1.call_count)
        self.assertEquals(1, counter2.call_count)

        payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472028637866,
        "messaging":[{
            "sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472028637825,
            "message":{"quick_reply":{"payload":"PICK_COMEDY"},"mid":"mid.1472028637817:ae2763cc036a664b43","seq":834,"text":"Action"}}]}]}
        """
        self.page.handle_webhook(payload, postback=handler1)
        self.assertEquals(2, counter1.call_count)
        self.assertEquals(1, counter2.call_count)

    def test_callback_regex_pattern(self):
        payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472028637866,
        "messaging":[{
            "sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472028637825,
            "message":{"quick_reply":{"payload":"ACTION/1"},"mid":"mid.1472028637817:ae2763cc036a664b43","seq":834,"text":"Action"}}]}]}
        """

        counter1 = mock.MagicMock()

        @self.page.callback(['ACTION'], types=['QUICK_REPLY'])
        def callback(payload, event):
            counter1()

        self.page.handle_webhook(payload)

        self.assertEquals(0, counter1.call_count)

        @self.page.callback(['ACTION/(.+)'], types=['QUICK_REPLY'])
        def callback2(payload, event):
            counter1()

        self.page.handle_webhook(payload)

        self.assertEquals(1, counter1.call_count)

    def test_callback_types(self):
        counter1 = mock.MagicMock()
        counter2 = mock.MagicMock()
        counter3 = mock.MagicMock()

        quickreply_payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472028637866,
        "messaging":[{
            "sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472028637825,
            "message":{"quick_reply":{"payload":"ACTION/1"},"mid":"mid.1472028637817:ae2763cc036a664b43","seq":834,"text":"Action"}}]}]}
        """

        button_payload = """
        {"object":"page","entry":[{"id":"1691462197845448","time":1472028006107,
        "messaging":[{
            "sender":{"id":"1134343043305865"},"recipient":{"id":"1691462197845448"},"timestamp":1472028006107,
            "postback":{"payload":"ACTION/100"}}]
        }]}
        """

        @self.page.callback(['ACTION/(.+)'])
        def callback(payload, event):
            counter1()

        @self.page.callback(['ACTION(.+)'], types=['QUICK_REPLY'])
        def callback2(payload, event):
            counter2()

        @self.page.callback(['ACTIO(.+)'], types=['POSTBACK'])
        def callback3(payload, event):
            counter3()

        self.page.handle_webhook(quickreply_payload)
        self.assertEquals(1, counter1.call_count)
        self.assertEquals(1, counter2.call_count)
        self.assertEquals(0, counter3.call_count)
        self.page.handle_webhook(button_payload)
        self.assertEquals(2, counter1.call_count)
        self.assertEquals(1, counter2.call_count)
        self.assertEquals(1, counter3.call_count)

        with self.assertRaises(ValueError):
            @self.page.callback(['ACTIO(.+)'], types=['LSKDJFLKSJFD'])
            def callback4(payload, event):
                counter3()

    def test_greeting(self):
        exp = """
            {
                "greeting": [
                    {
                        "locale":"default",
                        "text":"hello"
                    }
                ]
            }
            """
        with MessengerAPIMock(subpath="messenger_profile", expected=exp,
                              utest=self) as m:
            self.page.greeting("hello")

        with MessengerAPIMock(subpath="messenger_profile"):
            with self.assertRaises(ValueError):
                self.page.greeting(1)

    def test_localized_greeting(self):
        exp="""
            {
                "greeting": [
                    {
                        "locale":"default",
                        "text":"hello"
                    },
                    {
                        "locale":"en_US",
                        "text":"hello US"
                    }
                ]
            }
            """
        with MessengerAPIMock(subpath="messenger_profile", expected=exp,
                              utest=self) as m:
            self.page.localized_greeting(
                [LocalizedObj(locale="default", obj="hello"),
                 LocalizedObj(locale="en_US", obj="hello US")])

        with MessengerAPIMock(subpath="messenger_profile"):
            with self.assertRaises(ValueError):
                self.page.localized_greeting(
                    [LocalizedObj(locale="bad", obj="hello")])

    def test_hide_greeting(self):
        exp="""
        {
            "fields": [
                "greeting"
            ]
        }
        """
        with MessengerAPIMock(subpath="messenger_profile", expected=exp,
                              method=MessengerAPIMock.DELETE, utest=self) as m:
            self.page.hide_greeting()

    def test_starting_button(self):
        exp="""
        {
            "get_started": {
                "payload": "PAYLOAD"
            }
        }
        """
        with MessengerAPIMock(subpath="messenger_profile", expected=exp,
                              utest=self) as m:
            self.page.show_starting_button("PAYLOAD")

        with MessengerAPIMock(subpath="messenger_profile"):
            with self.assertRaises(ValueError):
                self.page.show_starting_button(1)

    def test_hide_starting_button(self):
        exp="""
        {
            "fields": [
                "get_started"
            ]
        }
        """
        with MessengerAPIMock(subpath="messenger_profile", expected=exp,
                              method=MessengerAPIMock.DELETE, utest=self) as m:
            self.page.hide_starting_button()

    def test_persistent_menu(self):
        exp = """
        {
            "persistent_menu": [
                {
                    "locale":"default",
                    "call_to_actions": [
                        {
                            "type": "postback",
                            "title": "yes",
                            "payload": "hobbang"
                        },
                        {
                            "type": "web_url",
                            "title": "url",
                            "url": "url"
                        },
                        {
                            "type": "postback",
                            "title": "ho",
                            "payload": "bbang"
                        }
                    ]
                }
            ]
        }
        """
        with MessengerAPIMock(subpath="messenger_profile", expected=exp,
                              utest=self) as m:
            self.page.show_persistent_menu(
                [{'type':'postback', 'title':'yes', 'payload':'hobbang'},
                 {'type':'web_url', 'title':'url', 'value':'url'},
                 Template.ButtonPostBack('ho', 'bbang')])

        with MessengerAPIMock(subpath="messenger_profile", expected=exp):
            with self.assertRaises(ValueError):
                self.page.show_persistent_menu("hi")

            with self.assertRaises(ValueError):
                self.page.show_persistent_menu([Template.ButtonPhoneNumber('ho', 'bbang'),
                                                Template.ButtonWeb('title', 'url')])

            with self.assertRaises(ValueError):
                self.page.show_persistent_menu([{'type':'ho'}])

    def test_localized_persistent_menu(self):
        exp = """
        {
            "persistent_menu": [
                {
                    "locale":"default",
                    "call_to_actions": [
                        {
                            "type": "postback",
                            "title": "yes",
                            "payload": "hobbang"
                        },
                        {
                            "type": "web_url",
                            "title": "url",
                            "url": "url"
                        },
                        {
                            "type": "postback",
                            "title": "ho",
                            "payload": "bbang"
                        }
                    ]
                },
                {
                    "locale":"zh_CN",
                    "call_to_actions": [
                        {
                            "type": "postback",
                            "title": "yes CN",
                            "payload": "hobbang_cn"
                        },
                        {
                            "type": "web_url",
                            "title": "url CN",
                            "url": "url_cn"
                        },
                        {
                            "type": "postback",
                            "title": "ho CN",
                            "payload": "bbang_cn"
                        }
                    ]
                }
            ]
        }
        """
        with MessengerAPIMock(subpath="messenger_profile", expected=exp,
                              utest=self) as m:
            self.page.show_localized_persistent_menu([
                LocalizedObj(
                    locale="default",
                    obj=[
                        {'type':'postback', 'title':'yes',
                         'payload':'hobbang'},
                        {'type':'web_url', 'title':'url', 'value':'url'},
                        Template.ButtonPostBack('ho', 'bbang')]),
                LocalizedObj(
                    locale="zh_CN",
                    obj=[
                        {'type': 'postback', 'title': 'yes CN',
                         'payload': 'hobbang_cn'},
                        {'type': 'web_url', 'title': 'url CN',
                         'value': 'url_cn'},
                        Template.ButtonPostBack('ho CN', 'bbang_cn')]),
            ])

    def test_hide_persistent_menu(self):
        exp="""
        {
            "fields": [
                "persistent_menu"
            ]
        }
        """
        with MessengerAPIMock(subpath="messenger_profile", expected=exp,
                              method=MessengerAPIMock.DELETE, utest=self) as m:
            self.page.hide_persistent_menu()

    def test_unsupported_entry(self):
        bug_str = """
        {
            "object":"page",
            "entry":[
                {
                    "id":"214236215771147",
                    "time":1502997235746,
                    "standby":[
                        {
                            "recipient":{
                                "id":"214236215771147"
                            },
                            "timestamp":1502997235746,
                            "sender":{
                                "id":"143792855957756q9"
                            },
                            "postback":{
                                "title":"Get Started"
                            }
                        }
                    ]
                }
            ]
        }
        """
        self.page.handle_webhook(bug_str)
