USER_ID, TG_ID, USER_TG_ID, NAME, SURNAME, USERNAME, FROM_REGION, FROM_DISTRICT, FROM_LOCATION = \
    ('user_id', 'tg_id', 'user_tg_id', 'name', 'surname', 'username', 'from_region', 'from_district', 'from_location')

TO_REGION, TO_DISTRICT, TO_LOCATION, RECEIVER_CONTACT, IS_ADMIN, YES_NO, PASSENGERS, PASSENGERS_TEXT = \
    ('to_region', 'to_district', 'to_location', 'receiver_contact', 'is_admin', 'yes_no', 'passengers',
     'passengers_text')

ASK_PARCEL, DEFINITION, DATETIME, DATE, TIME, PHONE_NUMBER_2, CONFIRMATION, EDITING, MESSAGE_ID = \
    ('ask_parcel', 'definition', 'datetime', 'date', 'time', 'phone_number_2', 'confirmation', 'editing', 'message_id')

FROM_TEXT, TO_TEXT, WEIGHT_TEXT, VOLUME_TEXT, COMMENT_TEXT, DATE_TEXT, POST_ID, FULLNAME = \
    ('from_text', 'to_text', 'weight_text', 'volume_text', 'comment_text', 'date_text', 'post_id', 'fullname')

DATETIME_TEXT, USER_TEXT, USER_PHONE_NUMBER_TEXT, STATE, REGION_NAME, ID, LANG, PHONE_NUMBER, REGION = \
    ('datetime_text', 'user_text', 'user_phone_number_text', 'state', 'region_name', 'id', 'lang', 'phone_number',
     'region')

STATUS_TEXT, OPENED_STATUS, CLOSED_STATUS, NOT_CONFIRMED_STATUS, TG_ACCOUNT_TEXT, UNDEFINED_TEXT = \
    ('status_text', 'opened_status', 'closed_status', 'not_confirmed_status', 'tg_account_text', 'undifened_text')

DISTRICT, COMMENT, PASSENGER_TEXT, ANNOUNCE, PARCEL, PASSENGER, STATUS, QUANTITY, DEPARTURE_TIME = \
    ('district', 'comment', 'passenger_text', 'announce', 'parcel', 'passenger', 'status', 'quantity', 'departure_time')

PARCEL_TEXT, RECEIVER_CONTACT_TEXT, SENDER_TEXT, CAR_MODEL, CAR_ID, BAGGAGE, CHECKED, EMPTY_SEATS = \
    ('parcel_text', 'receiver_contact_text', 'sender_text', 'car_model', 'car_id', 'baggage', 'checked', 'empty_seats')

TAXI_TEXT, EMPTY_SEATS_TEXT, DRIVER_TEXT, BAGGAGE_TEXT, DRIVER_ID, AGREEMENT, CHOOSE_EDITING = \
    ('taxi_text', 'empty_seats_text', 'driver_text', 'baggage_text', 'driver_id', 'agreement', 'choose_editing')

EDIT_EMPTY_SEATS, EDIT_DISTRICT, EDIT_REGION, EDIT_ASK_PARCEL, EDIT_DATE, EDIT_TIME, EDIT_COMMENT = \
    ('edit_empty_seats', 'edit_district', 'edit_region', 'edit_ask_parcel', 'edit_date', 'edit_time', 'edit_comment')

DELETE, EDIT_DATETIME, EDIT_COMPLETE, EDIT_CAR_MODEL, CHOOSE_EDITING_CAR_MODEL_OR_BAGGAGE = \
    ('delete', 'edit_datetime', 'edit_complete', 'edit_car_model', 'choose_editing_car_model_or_baggage')

EDIT_FULLNAME, EDIT_PHONE_NUMBERS, EDIT_PHONE_NUMBER_2, EDIT_BAGGAGE, CHOOSE_EDITING_FULLNAME_OR_PHONE_NUMBERS = \
    ('edit_fullname', 'edit_phone_numbers', 'edit_phone_number_2', 'edit_baggage',
     'choose_editing_fullname_or_phone_numbers')

ALL_DISTRICTS_TEXT, SEND_LOCATION, DRIVER_TG_ID = ('all_districts_text', 'send_location', 'driver_tg_id')
