import json

from songmam.facebook.entries.base import BaseMessaging
from songmam.facebook.entries.deliveries import DeliveriesEntry
from songmam.facebook.entries.messages import MessageEntry
from songmam.facebook.entries.postback import PostbackEntry
from songmam.facebook.entries.referral import ReferralEntry


class Event:
    entry: MessageEntry

    def __init__(self, entry):
        self.entry = entry
        self.sender = self.entry.theMessaging.sender
        self.recipient = self.entry.theMessaging.recipient

    def __str__(self):
        # TODO: some infomative
        return json.dumps(self.__class__.__name__)


class MessageEvent(Event):
    entry: MessageEntry

    @property
    def is_quick_reply(self):
        if self.entry.theMessaging.message.quick_reply:
            return True
        else:
            return False

    def __init__(self, entry):
        super(MessageEvent, self).__init__(entry)

        self.name = 'message'
        # self.message = self.entry.theMessaging.message
        self.text = self.entry.theMessaging.message.text
        self.message_id = self.entry.theMessaging.message.mid
        self.quick_reply = self.entry.theMessaging.message.quick_reply
        self.reply_to = self.entry.theMessaging.message.reply_to
        self.attachments = self.entry.theMessaging.message.attachments


class PostBackEvent(Event):
    entry: PostbackEntry

    def __init__(self, entry: PostbackEntry):
        super(PostBackEvent, self).__init__(entry)

        self.title = self.entry.theMessaging.postback.title
        self.payload = self.entry.theMessaging.postback.payload
        # self.referal = self.entry.postback.referral



class DeliveriesEvent(Event):
    entry: DeliveriesEntry

    def __init__(self, entry: DeliveriesEntry):
        super(DeliveriesEvent, self).__init__(entry)

        self.mids = self.entry.theMessaging.delivery.mids
        self.watermark = self.entry.theMessaging.delivery.watermark


class EchoEvent(Event):
    def __init__(self, message, **kwargs):
        super(EchoEvent, self).__init__(**kwargs)

        self.name = 'echo'
        self.message = message

    @property
    def mid(self):
        return self.message.get('mid')

    @property
    def app_id(self):
        return self.message.get('app_id')

    @property
    def metadata(self):
        return self.message.get('metadata')

    @property
    def text(self):
        return self.message.get('text')

    @property
    def attachments(self):
        return self.message.get('attachments')


class ReadEvent(Event):
    def __init__(self, read, **kwargs):
        super(ReadEvent, self).__init__(**kwargs)

        self.name = 'read'
        self.read = read

    @property
    def seq(self):
        return self.read.get('seq')

    @property
    def watermark(self):
        return self.read.get('watermark')


class AccountLinkingEvent(Event):
    def __init__(self, account_linking, **kwargs):
        super(AccountLinkingEvent, self).__init__(**kwargs)

        self.name = 'account_linking'
        self.account_linking = account_linking

    @property
    def status(self):
        return self.account_linking.get('status')

    @property
    def is_linked(self):
        return self.status == 'linked'

    @property
    def authorization_code(self):
        return self.account_linking.get('authorization_code')


class GamePlayEvent(Event):
    def __init__(self, game_play, **kwargs):
        super(GamePlayEvent, self).__init__(**kwargs)

        self.name = 'game_play'
        self.game_play = game_play

    @property
    def game_id(self):
        return self.game_play.get('game_id')

    @property
    def player_id(self):
        return self.game_play.get('player_id')

    @property
    def context_type(self):
        return self.game_play.get('context_type')

    @property
    def context_id(self):
        return self.game_play.get('context_id')

    @property
    def score(self):
        return self.game_play.get('score')

    @property
    def payload(self):
        return self.game_play.get('payload')


class PassThreadEvent(Event):
    def __init__(self, pass_thread_control, **kwargs):
        super(PassThreadEvent, self).__init__(**kwargs)

        self.name = 'pass_thread_control'
        self.pass_thread_control = pass_thread_control

    @property
    def new_owner_app_id(self):
        return self.pass_thread_control.get('new_owner_app_id')

    @property
    def metadata(self):
        return self.pass_thread_control.get('metadata')


class TakeThreadEvent(Event):
    def __init__(self, take_thread_control, **kwargs):
        super(TakeThreadEvent, self).__init__(**kwargs)

        self.name = 'take_thread_control'
        self.take_thread_control = take_thread_control

    @property
    def previous_owner_app_id(self):
        return self.take_thread_control.get('previous_owner_app_id')

    @property
    def metadata(self):
        return self.take_thread_control.get('metadata')


class RequestThreadEvent(Event):
    def __init__(self, request_thread_control, **kwargs):
        super(RequestThreadEvent, self).__init__(**kwargs)

        self.name = 'request_thread_control'
        self.request_thread_control = request_thread_control

    @property
    def requested_owner_app_id(self):
        return self.request_thread_control.get('requested_owner_app_id')

    @property
    def metadata(self):
        return self.request_thread_control.get('metadata')


class AppRoleEvent(Event):
    def __init__(self, app_roles, **kwargs):
        super(AppRoleEvent, self).__init__(**kwargs)

        self.name = 'app_roles'
        self.app_roles = app_roles


class OptinEvent(Event):
    def __init__(self, optin, **kwargs):
        super(OptinEvent, self).__init__(**kwargs)

        self.name = 'optin'
        self.optin = optin

    @property
    def ref(self):
        return self.optin.get('ref')

    @property
    def user_ref(self):
        return self.optin.get('user_ref')


class PolicyEnforcementEvent(Event):
    def __init__(self, policy_enforcement, **kwargs):
        super(PolicyEnforcementEvent, self).__init__(**kwargs)

        self.name = 'policy_enforcement'
        self.policy_enforcement = policy_enforcement

    @property
    def action(self):
        return self.policy_enforcement.get('action')

    @property
    def reason(self):
        return self.policy_enforcement.get('reason')


class ReferralEvent(Event):
    entry: ReferralEntry

    def __init__(self, entry):
        super(ReferralEvent, self).__init__(entry)
        self.referral = self.entry.referral

    # @property
    # def source(self):
    #     return self.referral.get('source')
    #
    # @property
    # def type(self):
    #     return self.referral.get('type')
    #
    # @property
    # def ref(self):
    #     return self.referral.get('ref')
    #
    # @property
    # def referer_uri(self):
    #     return self.referral.get('referer_uri')


class CheckOutUpdateEvent(Event):  # beta
    def __init__(self, checkout_update, **kwargs):
        super(CheckOutUpdateEvent, self).__init__(**kwargs)

        self.name = 'checkout_update'
        self.checkout_update = checkout_update

    @property
    def payload(self):
        return self.checkout_update.get('payload')

    @property
    def shipping_address(self):
        return self.checkout_update.get('shipping_address')


class PaymentEvent(Event):  # beta
    def __init__(self, payment, **kwargs):
        super(PaymentEvent, self).__init__(**kwargs)

        self.name = 'payment'
        self.payment = payment

    @property
    def payload(self):
        return self.payment.get('payload')

    @property
    def requested_user_info(self):
        return self.payment.get('requested_user_info')

    @property
    def payment_credential(self):
        return self.payment.get('payment_credential')

    @property
    def amount(self):
        return self.payment.get('amount')

    @property
    def shipping_option_id(self):
        return self.payment.get('shipping_option_id')


class StandByEvent(Event):
    def __init__(self, standby, **kwargs):
        super(StandByEvent, self).__init__(**kwargs)

        self.name = 'standby'
        self.standby = standby
