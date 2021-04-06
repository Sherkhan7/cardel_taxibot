from helpers import wrap_tags
from layouts.layoutdicts import *
from languages import LANGS
from DB import get_region_and_district, get_region_districts
from config import BOT_USERNAME
from inlinekeyboards.inlinekeyboardvariables import yes_no_keyboard
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
        f'🚶‍♂ {PASSENGER_LAYOUT_DICT[lang][PASSENGER_TEXT]}\n',
        f'📍 {PASSENGER_LAYOUT_DICT[lang][FROM_TEXT]}: {wrap_tags(from_district_name, from_region_name)}',
        f'🏁 {PASSENGER_LAYOUT_DICT[lang][TO_TEXT]}: {wrap_tags(to_district_name, to_region_name)}\n',
        f'🚶 {PASSENGER_LAYOUT_DICT[lang][PASSENGERS_TEXT]}: {wrap_tags(passengers)}',
        f'🕒 {PASSENGER_LAYOUT_DICT[lang][DATETIME_TEXT]}: {wrap_tags(date, time)}',
        f'📋 {PASSENGER_LAYOUT_DICT[lang][COMMENT_TEXT]}: {wrap_tags(comment)}',
        f'\n👤 {PASSENGER_LAYOUT_DICT[lang][USER_TEXT]}: {wrap_tags(fullanme)}',
        f'📞 {PASSENGER_LAYOUT_DICT[lang][USER_PHONE_NUMBER_TEXT]}: {wrap_tags(phone_number)}\n',
        f'🤖 @{BOT_USERNAME} ©',
        f'🛡 cardel online ™',
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
        f'📦 {PARCEL_LAYOUT_DICT[lang][PARCEL_TEXT]}\n',
        f'📍 {PASSENGER_LAYOUT_DICT[lang][FROM_TEXT]}: {wrap_tags(from_district_name, from_region_name)}',
        f'🏁 {PASSENGER_LAYOUT_DICT[lang][TO_TEXT]}: {wrap_tags(to_district_name, to_region_name)}\n',
        f'📞 {PARCEL_LAYOUT_DICT[lang][RECEIVER_CONTACT_TEXT]}: {wrap_tags(receiver_contact)}',
        f'📦 {PARCEL_LAYOUT_DICT[lang][PARCEL_TEXT]}: {wrap_tags(comment)}\n',
        f'👤 {PARCEL_LAYOUT_DICT[lang][SENDER_TEXT]}: {wrap_tags(fullname)}',
        f'📞 {PASSENGER_LAYOUT_DICT[lang][USER_PHONE_NUMBER_TEXT]}: {wrap_tags(phone_number)}\n',
        f'🤖 @{BOT_USERNAME} ©',
        f'🛡 cardel online ™',
    ]

    return '\n'.join(layout)


def get_active_driver_layout(lang, data):
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
        to += f'{to_region_name[0]} ({", ".join(to_districts_name)})\n'
        to_region_name.clear()
        to_districts_name.clear()

    fullname = data[FULLNAME]
    phone_number = data[PHONE_NUMBER]
    departure_time = data[DEPARTURE_TIME]
    comment = str(data[COMMENT])
    empty_seats = str(data[EMPTY_SEATS])
    car_model = data[CAR_MODEL]
    parcel = inline_keyboard_types[yes_no_keyboard][0][f'text_{lang}'] if data[ASK_PARCEL] \
        else inline_keyboard_types[yes_no_keyboard][1][f'text_{lang}']
    baggage = inline_keyboard_types[yes_no_keyboard][2][f'text_{lang}'] if data[BAGGAGE] else \
        inline_keyboard_types[yes_no_keyboard][1][f'text_{lang}']

    layout = [
        f'🚕 {TAXI_LAYOUT_DICT[lang][TAXI_TEXT]}\n',
        f'📍 {PASSENGER_LAYOUT_DICT[lang][FROM_TEXT]}: {wrap_tags(from_)}',
        f'🏁 {PASSENGER_LAYOUT_DICT[lang][TO_TEXT]}: {wrap_tags(to)}\n',
        f'🚖 {TAXI_LAYOUT_DICT[lang][EMPTY_SEATS_TEXT]}: {wrap_tags(empty_seats)}',
        f'📦 {TAXI_LAYOUT_DICT[lang][ASK_PARCEL]}: {wrap_tags(parcel)}',
        f'📋 {PASSENGER_LAYOUT_DICT[lang][COMMENT_TEXT]}: {wrap_tags(comment)}',
        f'🕒 {PASSENGER_LAYOUT_DICT[lang][DATETIME_TEXT]}: {wrap_tags(departure_time)}\n',
        f'👤 {TAXI_LAYOUT_DICT[lang][DRIVER_TEXT]}: {wrap_tags(fullname)}',
        f'📞 {PASSENGER_LAYOUT_DICT[lang][USER_PHONE_NUMBER_TEXT]}: {wrap_tags(phone_number)}',
        f'🚖 {TAXI_LAYOUT_DICT[lang][BAGGAGE_TEXT]}: {wrap_tags(baggage)}',
        f'🚖 {TAXI_LAYOUT_DICT[lang][CAR_MODEL]}: {wrap_tags(car_model)}\n',
        f'🤖 @{BOT_USERNAME} ©',
        f'🛡 cardel online ™',
    ]
    if data[COMMENT] is None:
        layout.pop(5)

    return '\n'.join(layout)


def get_fullname_error_text(lang):
    if lang == LANGS[0]:
        text = "Ism,familya xato yuborildi!\n" \
               "Qaytadan quyidagi formatda yuboring"
        example = "Misol: Sherzodbek Esanov yoki Sherzodbek"

    if lang == LANGS[1]:
        text = "Имя,фамилия введено неверное!\n" \
               "Отправьте еще раз в следующем формате"
        example = 'Пример: Шерзодбек Эсанов или Шерзодбек'

    if lang == LANGS[2]:
        text = "Исм,фамиля хато юборилди!\n" \
               "Қайтадан қуйидаги форматда юборинг"
        example = "Мисол: Шерзодбек Эсанов ёки Шерзодбек"

    return f'⚠  {text}:\n\n {wrap_tags(example)}'


def get_phone_number_error_text(lang):
    if lang == LANGS[0]:
        text = "Telefon raqami xato formatda yuborildi"

    if lang == LANGS[1]:
        text = "Номер телефона введен в неправильном формате"

    if lang == LANGS[2]:
        text = "Телефон рақами хато форматда юборилди"

    return text


def get_phone_number_layout(lang):
    """ Layout view
        telefon raqamini quyidagi formatda yuboring

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
        text = "Если у вас есть какие-либо комментарии, пожалуйста, напишите"
        button_text = "Нет комментариев"

    if lang == LANGS[2]:
        text = "Агар изоҳларингиз бўлса ёзиб юборинг"
        button_text = "Изоҳ йўқ"

    return [f'{text}:', button_text]
