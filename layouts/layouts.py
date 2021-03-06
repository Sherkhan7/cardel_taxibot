from helpers import wrap_tags
from layouts.layoutdicts import *
from languages import LANGS
from DB import get_region_and_district, get_region_districts, get_region_discricts_num
from config import BOT_USERNAME
from inlinekeyboards.inlinekeyboardvariables import yes_no_keyboard, back_next_keyboard
from inlinekeyboards.inlinekeyboardtypes import inline_keyboard_types


def get_passenger_layout(lang, data):
    from_point = get_region_and_district(data[FROM_REGION], data[FROM_DISTRICT])
    from_region_name = from_point[0][f'name_{lang}']
    from_district_name = from_point[1][f'name_{lang}']

    to_point = get_region_and_district(data[TO_REGION], data[TO_DISTRICT])
    to_region_name = to_point[0][f'name_{lang}']
    to_district_name = to_point[1][f'name_{lang}']

    date = data[DATE]
    time = data[TIME]
    comment = str(data[COMMENT])
    fullanme = data[FULLNAME]
    phone_number = data[PHONE_NUMBER]
    passengers = str(data[PASSENGERS])

    if time == 'now':
        time = PASSENGER_LAYOUT_DICT[lang][TIME]

    layout = [
        f'πΆββ {PASSENGER_LAYOUT_DICT[lang][PASSENGER_TEXT]}\n',
        f'π {PASSENGER_LAYOUT_DICT[lang][FROM_TEXT]}: {wrap_tags(from_district_name, from_region_name)}',
        f'π {PASSENGER_LAYOUT_DICT[lang][TO_TEXT]}: {wrap_tags(to_district_name, to_region_name)}\n',
        f'πΆ {PASSENGER_LAYOUT_DICT[lang][PASSENGERS_TEXT]}: {wrap_tags(passengers)}',
        f'π {PASSENGER_LAYOUT_DICT[lang][DATETIME_TEXT]}: {wrap_tags(date, time)}',
        f'π {PASSENGER_LAYOUT_DICT[lang][COMMENT_TEXT]}: {wrap_tags(comment)}',
        f'\nπ€ {PASSENGER_LAYOUT_DICT[lang][USER_TEXT]}: {wrap_tags(fullanme)}',
        f'π {PASSENGER_LAYOUT_DICT[lang][USER_PHONE_NUMBER_TEXT]}: {wrap_tags(phone_number)}\n',
        f'π€ @{BOT_USERNAME} Β©',
    ]
    if data[COMMENT] is None:
        layout.pop(5)

    return '\n'.join(layout)


def get_parcel_layout(lang, data):
    from_point = get_region_and_district(data[FROM_REGION], data[FROM_DISTRICT])
    from_region_name = from_point[0][f'name_{lang}']
    from_district_name = from_point[1][f'name_{lang}']

    to_point = get_region_and_district(data[TO_REGION], data[TO_DISTRICT])
    to_region_name = to_point[0][f'name_{lang}']
    to_district_name = to_point[1][f'name_{lang}']

    receiver_contact = data[RECEIVER_CONTACT]
    comment = data[COMMENT]
    fullname = data[FULLNAME]
    phone_number = data[PHONE_NUMBER]

    layout = [
        f'π¦ {PARCEL_LAYOUT_DICT[lang][PARCEL_TEXT]}\n',
        f'π {PASSENGER_LAYOUT_DICT[lang][FROM_TEXT]}: {wrap_tags(from_district_name, from_region_name)}',
        f'π {PASSENGER_LAYOUT_DICT[lang][TO_TEXT]}: {wrap_tags(to_district_name, to_region_name)}\n',
        f'π {PARCEL_LAYOUT_DICT[lang][RECEIVER_CONTACT_TEXT]}: {wrap_tags(receiver_contact)}',
        f'π¦ {PARCEL_LAYOUT_DICT[lang][PARCEL_TEXT]}: {wrap_tags(comment)}\n',
        f'π€ {PARCEL_LAYOUT_DICT[lang][SENDER_TEXT]}: {wrap_tags(fullname)}',
        f'π {PASSENGER_LAYOUT_DICT[lang][USER_PHONE_NUMBER_TEXT]}: {wrap_tags(phone_number)}\n',
        f'π€ @{BOT_USERNAME} Β©',
    ]

    return '\n'.join(layout)


def get_active_driver_layout(lang, data, label=None):
    checked = data[CHECKED]
    from_region_name = []
    from_districts_name = []
    from_ = ''
    for region_id, districts_list in checked['from'].items():
        for region in get_region_districts(region_id, districts_list):
            if region['parent_id'] == 0:
                from_region_name.append(region[f'name_{lang}'])
            else:
                from_districts_name.append(region[f'name_{lang}'])

        if get_region_discricts_num(region_id)['num'] == len(from_districts_name):
            from_ += f'{from_region_name[0]} ({TAXI_LAYOUT_DICT[lang][ALL_DISTRICTS_TEXT]})\n'
        else:
            from_ += f'{from_region_name[0]} ({", ".join(from_districts_name)})\n'

        from_region_name.clear()
        from_districts_name.clear()

    to_region_name = []
    to_districts_name = []
    to = ''
    for region_id, districts_list in checked['to'].items():
        for region in get_region_districts(region_id, districts_list):
            if region['parent_id'] == 0:
                to_region_name.append(region[f'name_{lang}'])
            else:
                to_districts_name.append(region[f'name_{lang}'])

        if get_region_discricts_num(region_id)['num'] == len(to_districts_name):
            to += f'{to_region_name[0]} ({TAXI_LAYOUT_DICT[lang][ALL_DISTRICTS_TEXT]})\n'
        else:
            to += f'{to_region_name[0]} ({", ".join(to_districts_name)})\n'

        to_region_name.clear()
        to_districts_name.clear()

    fullname = data[FULLNAME]
    phone_number = data[PHONE_NUMBER]
    date = data[DATE]
    time = data[TIME]
    empty_seats = str(data[EMPTY_SEATS])
    car_model = data[CAR_MODEL]
    parcel = inline_keyboard_types[yes_no_keyboard][0][f'text_{lang}'] if data[ASK_PARCEL] \
        else inline_keyboard_types[yes_no_keyboard][1][f'text_{lang}']
    baggage = inline_keyboard_types[yes_no_keyboard][2][f'text_{lang}'] if data[BAGGAGE] else \
        inline_keyboard_types[yes_no_keyboard][1][f'text_{lang}']

    if time == 'now':
        time = PASSENGER_LAYOUT_DICT[lang][TIME]
    elif time == 'undefined':
        time = inline_keyboard_types[back_next_keyboard][2][f'text_{lang}']

    label = f'[{label}]' if label else ''
    comment = '\n' if data[COMMENT] is None else \
        f'\nπ¬ {PASSENGER_LAYOUT_DICT[lang][COMMENT_TEXT]}: {wrap_tags(data[COMMENT])}\n'
    phone_number_2 = '' if data[PHONE_NUMBER_2] is None else \
        f'\nπ {PASSENGER_LAYOUT_DICT[lang][USER_PHONE_NUMBER_TEXT]}: {wrap_tags(data[PHONE_NUMBER_2])}'

    layout = [
        f'π {TAXI_LAYOUT_DICT[lang][TAXI_TEXT]} {label}\n',
        f'π {PASSENGER_LAYOUT_DICT[lang][FROM_TEXT]}: {wrap_tags(from_)}',
        f'π {PASSENGER_LAYOUT_DICT[lang][TO_TEXT]}: {wrap_tags(to)}',
        f'π {TAXI_LAYOUT_DICT[lang][EMPTY_SEATS_TEXT]}: {wrap_tags(empty_seats)}',
        f'π¦ {TAXI_LAYOUT_DICT[lang][ASK_PARCEL]}: {wrap_tags(parcel)}',
        f'π {PASSENGER_LAYOUT_DICT[lang][DATETIME_TEXT]}: {wrap_tags(date, time)}'
        f'{comment}',
        f'π€ {TAXI_LAYOUT_DICT[lang][DRIVER_TEXT]}: {wrap_tags(fullname)}',
        f'π {PASSENGER_LAYOUT_DICT[lang][USER_PHONE_NUMBER_TEXT]}: {wrap_tags(phone_number)}'
        f'{phone_number_2}',
        f'π {TAXI_LAYOUT_DICT[lang][BAGGAGE_TEXT]}: {wrap_tags(baggage)}',
        f'π {TAXI_LAYOUT_DICT[lang][CAR_MODEL]}: {wrap_tags(car_model)}\n',
        f'π€ @{BOT_USERNAME} Β©',
    ]

    return '\n'.join(layout)


def get_fullname_error_text(lang):
    if lang == LANGS[0]:
        text = "Ism xato yuborildi !\n" \
               "Qaytadan quyidagi formatda yuboring"
        example = "Misol: Sherzodbek Esanov yoki Sherzodbek"

    if lang == LANGS[1]:
        text = "ΠΠΌΡ Π²Π²Π΅Π΄Π΅Π½ΠΎ Π½Π΅Π²Π΅ΡΠ½ΠΎΠ΅ !\n" \
               "ΠΡΠΏΡΠ°Π²ΡΡΠ΅ Π΅ΡΠ΅ ΡΠ°Π· Π² ΡΠ»Π΅Π΄ΡΡΡΠ΅ΠΌ ΡΠΎΡΠΌΠ°ΡΠ΅"
        example = 'ΠΡΠΈΠΌΠ΅Ρ: Π¨Π΅ΡΠ·ΠΎΠ΄Π±Π΅ΠΊ Π­ΡΠ°Π½ΠΎΠ² ΠΈΠ»ΠΈ Π¨Π΅ΡΠ·ΠΎΠ΄Π±Π΅ΠΊ'

    if lang == LANGS[2]:
        text = "ΠΡΠΌ ΡΠ°ΡΠΎ ΠΊΠΈΡΠΈΡΠΈΠ»Π΄ΠΈ !\n" \
               "?Π°ΠΉΡΠ°Π΄Π°Π½ ?ΡΠΉΠΈΠ΄Π°Π³ΠΈ ΡΠΎΡΠΌΠ°ΡΠ΄Π° ΡΠ±ΠΎΡΠΈΠ½Π³"
        example = "ΠΠΈΡΠΎΠ»: Π¨Π΅ΡΠ·ΠΎΠ΄Π±Π΅ΠΊ Π­ΡΠ°Π½ΠΎΠ² ΡΠΊΠΈ Π¨Π΅ΡΠ·ΠΎΠ΄Π±Π΅ΠΊ"

    return f'β   {text}:\n\n {wrap_tags(example)}'


def get_phone_number_error_text(lang):
    if lang == LANGS[0]:
        text = "Telefon raqami xato formatda yuborildi"

    if lang == LANGS[1]:
        text = "ΠΠΎΠΌΠ΅Ρ ΡΠ΅Π»Π΅ΡΠΎΠ½Π° Π²Π²Π΅Π΄Π΅Π½ Π² Π½Π΅ΠΏΡΠ°Π²ΠΈΠ»ΡΠ½ΠΎΠΌ ΡΠΎΡΠΌΠ°ΡΠ΅"

    if lang == LANGS[2]:
        text = "Π’Π΅Π»Π΅ΡΠΎΠ½ ΡΠ°?Π°ΠΌΠΈ ΡΠ°ΡΠΎ ΡΠΎΡΠΌΠ°ΡΠ΄Π° ΡΠ±ΠΎΡΠΈΠ»Π΄ΠΈ"

    return text


def get_phone_number_layout(lang):
    """ Layout view
        Telefon raqamini quyidagi formatda yuboring

        Misol: +998 XX xxx xx xx yoki XX xxx xx xx
    """
    return f"{PHONE_NUMBER_LAYOUT_DICT[lang][1]}:\n\n" \
           f"{PHONE_NUMBER_LAYOUT_DICT[lang][2]}: " \
           f"{wrap_tags('+998 XX xxx xx xx')} {PHONE_NUMBER_LAYOUT_DICT[lang][3]} {wrap_tags('XX xxx xx xx')}"


def get_comment_text(lang):
    if lang == LANGS[0]:
        text = "Agar izohlaringiz bo'lsa yozib yuboring"
        button_text = "Izoh yo'q"

    if lang == LANGS[1]:
        text = "ΠΡΠ»ΠΈ Ρ Π²Π°Ρ Π΅ΡΡΡ ΠΊΠ°ΠΊΠΈΠ΅-Π»ΠΈΠ±ΠΎ ΠΊΠΎΠΌΠΌΠ΅Π½ΡΠ°ΡΠΈΠΈ, ΠΏΠΎΠΆΠ°Π»ΡΠΉΡΡΠ°, Π½Π°ΠΏΠΈΡΠΈΡΠ΅"
        button_text = "ΠΠ΅Ρ ΠΊΠΎΠΌΠΌΠ΅Π½ΡΠ°ΡΠΈΠ΅Π²"

    if lang == LANGS[2]:
        text = "ΠΠ³Π°Ρ ΠΈΠ·ΠΎ?³Π»Π°ΡΠΈΠ½Π³ΠΈΠ· Π±ΡΠ»ΡΠ° ΡΠ·ΠΈΠ± ΡΠ±ΠΎΡΠΈΠ½Π³"
        button_text = "ΠΠ·ΠΎ?³ ΠΉΡ?"

    return [f'{text}:', button_text]


def get_user_data_and_driver_layout(user, driver):
    user_phone_number_2 = user[PHONE_NUMBER_2] if user[PHONE_NUMBER_2] is not None else \
        inline_keyboard_types[yes_no_keyboard][1][f'text_{user[LANG]}']

    user_data_layout = f"{wrap_tags(USER_INFO_LAYOUT_DICT[user[LANG]]['user_caption_text'])}:\n" \
                       f"{USER_INFO_LAYOUT_DICT[user[LANG]][FULLNAME]}: {user[FULLNAME]}\n\n" \
                       f"{USER_INFO_LAYOUT_DICT[user[LANG]][PHONE_NUMBER]}: {user[PHONE_NUMBER]}\n\n" \
                       f"{USER_INFO_LAYOUT_DICT[user[LANG]][PHONE_NUMBER_2]}: {user_phone_number_2}"

    if driver:
        baggage = inline_keyboard_types[yes_no_keyboard][2][f'text_{user[LANG]}'] if driver[BAGGAGE] else \
            inline_keyboard_types[yes_no_keyboard][1][f'text_{user[LANG]}']

        driver_layout = f"{wrap_tags(USER_INFO_LAYOUT_DICT[user[LANG]]['driver_caption_text'])}:\n" \
                        f"{TAXI_LAYOUT_DICT[user[LANG]][CAR_MODEL]}: {driver[CAR_MODEL]}\n\n" \
                        f"{TAXI_LAYOUT_DICT[user[LANG]][BAGGAGE_TEXT]}: {baggage}\n\n" \
                        f"{PASSENGER_LAYOUT_DICT[user[LANG]][STATUS_TEXT]}: {driver[STATUS]}"
    else:
        driver_layout = f"{wrap_tags(USER_INFO_LAYOUT_DICT[user[LANG]]['driver_caption_text'])}:\n" \
                        f"{inline_keyboard_types[yes_no_keyboard][1][f'text_{user[LANG]}']}"

    return user_data_layout + '\n\n' + driver_layout


def get_only_driver_layout(driver, lang):
    if driver:
        baggage = inline_keyboard_types[yes_no_keyboard][2][f'text_{lang}'] if driver[BAGGAGE] else \
            inline_keyboard_types[yes_no_keyboard][1][f'text_{lang}']

        driver_layout = f"{wrap_tags(USER_INFO_LAYOUT_DICT[lang]['driver_caption_text'])}:\n" \
                        f"{TAXI_LAYOUT_DICT[lang][CAR_MODEL]}: {driver[CAR_MODEL]}\n\n" \
                        f"{TAXI_LAYOUT_DICT[lang][BAGGAGE_TEXT]}: {baggage}\n\n" \
                        f"{PASSENGER_LAYOUT_DICT[lang][STATUS_TEXT]}: {driver[STATUS]}"
    else:
        driver_layout = f"{wrap_tags(USER_INFO_LAYOUT_DICT[lang]['driver_caption_text'])}:\n" \
                        f"{inline_keyboard_types[yes_no_keyboard][1][f'text_{lang}']}"

    return driver_layout


def get_only_user_data_layout(user):
    user_phone_number_2 = user[PHONE_NUMBER_2] if user[PHONE_NUMBER_2] is not None else \
        inline_keyboard_types[yes_no_keyboard][1][f'text_{user[LANG]}']

    user_data_layout = f"{wrap_tags(USER_INFO_LAYOUT_DICT[user[LANG]]['user_caption_text'])}:\n" \
                       f"{USER_INFO_LAYOUT_DICT[user[LANG]][FULLNAME]}: {user[FULLNAME]}\n\n" \
                       f"{USER_INFO_LAYOUT_DICT[user[LANG]][PHONE_NUMBER]}: {user[PHONE_NUMBER]}\n\n" \
                       f"{USER_INFO_LAYOUT_DICT[user[LANG]][PHONE_NUMBER_2]}: {user_phone_number_2}"

    return user_data_layout
