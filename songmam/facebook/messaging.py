# https://developers.facebook.com/docs/messenger-platform/send-messages#send_api_basics
from typing import Literal, List, Optional, Union

from pydantic import BaseModel, HttpUrl

from songmam.facebook.entries.base import ThingWithID


#  QUICK REPLIES START
from songmam.facebook.send import SendRecipient


class QuickReplies(BaseModel):
    content_type: Literal["text", "location", "user_phone_number", "user_email"]
    title: Optional[str]  # Required if content_type is 'text'
    payload: Optional[Union[str, int]]  # "payload":"<POSTBACK_PAYLOAD>"
    image_url: Optional[HttpUrl]  # Required if title is an empty string.


class SendingQuickRepliesMessage(BaseModel):
    text: str
    quick_replies: List[QuickReplies]


class SendingQuickRepliesEntry(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/buttons/quick-replies
    """
    recipient: ThingWithID
    messaging_type: Literal["RESPONSE"]
    message: SendingQuickRepliesMessage


#  END OF QUICK REPLIES

###############################################################

#  TEMPLATES START
class DefaultAction(BaseModel):
    """ # Mentioned as URL Button with no 'title'
    https://developers.facebook.com/docs/messenger-platform/reference/buttons/url
    """
    type: Literal["web_url"]
    url: HttpUrl
    webview_height_ratio: Optional[Literal["compact", "tall", "full"]]
    messenger_extensions: Optional[bool]
    fallback_url: HttpUrl
    webview_share_button: Optional[str]


class URLButton(DefaultAction):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/buttons/url
    """
    title: str


class PostbackButton(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/send-messages/buttons#postback
    """
    type: Literal["postback"]
    title: str
    payload: str


class CallButton(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/send-messages/buttons#call
    """
    type: Literal["phone_number"]
    title: str
    payload: str


class LogInButton(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/send-messages/buttons#login
    """
    type: Literal["account_link"]
    url: HttpUrl  # Authentication callback URL. Must use HTTPS protocol.


class LogOutButton(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/buttons/logout
    """
    type: Literal["account_unlink"]


class GameMetadata(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/buttons/game-play#game_metadata
    """
    player_id: Optional[str]
    context_id: Optional[str]


class GamePlayButton(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/buttons/game-play
    """
    type: Literal["game_play"]
    title: str
    payload: Optional[str]
    game_metadata: Optional[GameMetadata]


class Buttons(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/buttons/url#properties
    """
    type: Literal["web_url", "postback", "phone_number", "account_link", "account_unlink", "game_play"]
    title: str
    payload: Optional[str]  # for type : postback / phone_number / game_play
    url: Optional[HttpUrl]  # for type: web_url / LogIn
    webview_height_ratio: Optional[Literal["compact", "tall", "full"]]  # for type: web_url
    messenger_extensions: Optional[bool]  # for type: web_url
    fallback_url: Optional[HttpUrl]  # for type: web_url
    webview_share_button: Optional[str]  # for type: web_url
    game_metadata: Optional[GameMetadata]  # for type : game_play



class PayloadButton(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/button
    """
    template_type: Literal["button"]
    text: str
    buttons: List[Buttons]  # Set of 1-3 buttons that appear as call-to-actions.


class GenericElements(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/generic#elements
    """
    title: str
    subtitle: Optional[str]
    image_url: Optional[HttpUrl]
    default_action: Optional[DefaultAction]
    buttons: Optional[List[Buttons]]


class PayloadGeneric(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/generic
    """
    template_type: Literal["generic"]
    image_aspect_ratio: Optional[Literal["horizontal", "square"]]
    elements: List[GenericElements]


#  Media
class MediaElements(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/media#elements
    """
    media_type: Optional[Literal["image", "video"]]
    attachment_id: Optional[str]  # Cannot be used if url is set.
    url: Optional[str]  # Cannot be used if attachment_id is set.
    buttons: Optional[List[Buttons]]  # A maximum of 1 button is supported.


class PayloadMedia(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/media#payload
    """
    template_type: Literal["media"]
    elements: List[MediaElements]
    sharable: Optional[bool]


# Receipt
class ReceiptElements(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/receipt#elements
    """
    title: str
    subtitle: Optional[str]
    quantity: Optional[str]
    price: int  # The price of the item. For free items, '0' is allowed.
    currency: Optional[str]
    image_url: Optional[HttpUrl]


class Address(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/receipt#address
    """
    street_1: str
    street_2: Optional[str]
    city: str
    postal_code: str
    state: str
    country: str


class Summary(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/receipt#summary
    """
    subtotal: Optional[int]
    shipping_cost: Optional[int]
    total_tax: Optional[int]
    total_cost: int


class Adjustments(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/receipt#adjustments
    """
    name: str
    amount: int



class PayloadReceipt(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/receipt
    """
    template_type: Literal["receipt"]
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


# Receipt Airline Boarding Pass
class AuxiliaryFields(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-boarding-pass#auxiliary_field
    """
    label: str
    value: str


class SecondaryFields(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-boarding-pass#secondary_field
    """
    label: str
    value: str


class DepartureAirport(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-itinerary#departure_airport
    """
    airport_code: str
    city: str
    terminal: str
    gate: str


class ArrivalAirport(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-itinerary#arrival_airport
    """
    airport_code: str
    city: str


class FlightSchedule(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-itinerary#flight_schedule
    """
    boarding_time: Optional[str]
    departure_time: str
    arrival_time: Optional[str]


class FlightInfo(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-itinerary#flight_info
    """
    flight_number: str
    departure_airport: DepartureAirport
    arrival_airport: ArrivalAirport
    flight_schedule: FlightSchedule


class BoardingPass(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-boarding-pass#boarding_pass
    """
    passenger_name: str
    pnr_number: str
    travel_class: Optional[str]
    seat: Optional[str]
    auxiliary_fields: Optional[List[AuxiliaryFields]]
    secondary_fields: Optional[List[SecondaryFields]]
    logo_image_url: str
    header_image_url: Optional[str]
    header_text_field: Optional[str]  # in ref is "field" /// Optional. Text for the header field.
    qr_code: Optional[str]  # Not available if barcode_image_urlis used.
    barcode_image_url: Optional[str]  # Not available if qr_code is used.
    above_bar_code_image_url: Optional[str]
    flight_info: FlightInfo


class PayloadAirlineBoardingPass(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-boarding-pass
    """
    template_type: Literal["airline_boardingpass"]
    intro_message: str
    locale: str
    theme_color: Optional[str]
    boarding_pass: List[BoardingPass]


class PayloadAirlineCheckin(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-checkin
    """
    template_type: Literal["airline_checkin"]
    intro_message: str
    locale: str
    pnr_number: Optional[str]
    checkin_url: str
    flight_info: List[FlightInfo]


class PassengerInfo(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-itinerary#passenger_info
    """
    passenger_id: str
    ticket_number: Optional[str]
    name: str


class ProductInfo(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-itinerary#product_info
    """
    title: str
    value: str


class PassengerSegmentInfo(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-itinerary#passenger_segment_info
    """
    segment_id: str
    passenger_id: PassengerInfo.passenger_id
    seat: str
    seat_type: str
    product_info: Optional[List[ProductInfo]]  # List of products the passenger purchased. Maximum of 4 items is supported.


class PriceInfo(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-itinerary#price_info
    """
    title: str
    amount: int
    currency: Optional[str]


class PayloadAirlineItinerary(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-itinerary
    """
    template_type: Literal["airline_itinerary"]
    intro_message: str
    locale: str
    theme_color: Optional[str]
    pnr_number: str
    passenger_info: List[PassengerInfo]
    flight_info: List[FlightInfo]
    passenger_segment_info: List[PassengerSegmentInfo]
    price_info: Optional[List[PriceInfo]]
    base_price: Optional[int]
    tax: Optional[int]
    total_price: int
    currency: str


class UpdateFlightInfo(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-flight-update#update_flight_info
    """
    flight_number: str
    departure_airport: DepartureAirport
    arrival_airport: ArrivalAirport
    flight_schedule: FlightSchedule


class PayloadAirlineUpdate(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-flight-update#payload
    """
    template_type: Literal["airline_update"]
    intro_message: str
    theme_color: Optional[str]
    update_type: Literal["delay", "gate_change", "cancellation"]
    locale: str
    pnr_number: Optional[str]
    update_flight_info: UpdateFlightInfo


class SendingAMessageTemplateAttachment(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-flight-update#attachment
    """
    type: Literal["template"]
    payload: List[PayloadButton,
                  PayloadGeneric,
                  PayloadMedia,
                  PayloadReceipt,
                  PayloadAirlineBoardingPass,
                  PayloadAirlineCheckin,
                  PayloadAirlineItinerary,
                  PayloadAirlineUpdate]


class SendingAMessageTemplate(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-flight-update#message
    """
    attachment: SendingAMessageTemplateAttachment


class SendingAMessageTemplateEntry(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/airline-flight-update#attachment
    """
    recipient: SendRecipient
    message: SendingAMessageTemplate
