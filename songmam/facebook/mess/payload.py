from enum import auto
from typing import Literal, List, Union, Optional

from pydantic import BaseModel, HttpUrl, validator

from songmam.facebook.mess.buttons import DefaultAction, URLButton, PostBackButton, CallButton, LogInButton, \
    LogOutButton, GamePlayButton
from songmam.facebook.send import SendRecipient

ButtonTypeList = Union[URLButton, PostBackButton, CallButton, LogInButton, LogOutButton, GamePlayButton]


class PayloadButton(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/button
    """
    template_type: Literal["button"]
    text: str
    buttons: List[ButtonTypeList]  # Set of 1-3 buttons that appear as call-to-actions.

    @validator('buttons')
    def buttons_limit_to_3_buttons(cls, v):
        if len(v) > 3:
            raise ValueError('Maximum 3 buttons for Button Template.')
        elif len(v) == 0:
            raise ValueError('Set at least 1 button for Button Template.')
        return v


class GenericElements(BaseModel):
    """
    https://developers.facebook.com/docs/messenger-platform/reference/templates/generic#elements
    """
    title: str
    subtitle: Optional[str]
    image_url: Optional[HttpUrl]
    default_action: Optional[DefaultAction]
    buttons: Optional[List[ButtonTypeList]]


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
    buttons: Optional[List[ButtonTypeList]]  # A maximum of 1 button is supported.

    @validator('buttons')
    def buttons_limit_to_3_buttons(cls, v):
        if len(v) > 3:
            raise ValueError('Max buttons at 3 for Button Template.')
        return v


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
    product_info: Optional[
        List[ProductInfo]]  # List of products the passenger purchased. Maximum of 4 items is supported.


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
    payload: List[Union[PayloadButton,
                        PayloadGeneric,
                        PayloadMedia,
                        PayloadReceipt,
                        PayloadAirlineBoardingPass,
                        PayloadAirlineCheckin,
                        PayloadAirlineItinerary,
                        PayloadAirlineUpdate]]


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


from songmam.utils import AutoNameLower


class SenderAction(AutoNameLower):
    """https://developers.facebook.com/docs/messenger-platform/send-messages/sender-actions"""
    TYPING_ON = auto()
    TYPING_OFF = auto()
    MARK_SEEN = auto()
