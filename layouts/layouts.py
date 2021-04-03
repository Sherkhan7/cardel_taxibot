from helpers import wrap_tags
from layouts.layoutdicts import *
from languages import LANGS
from DB import get_region_and_district
from config import BOT_USERNAME


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


def get_mail_layout(lang, data):
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
        f'📦 {MAIL_LAYOUT_DICT[lang][MAIL_TEXT]}\n',
        f'📍 {PASSENGER_LAYOUT_DICT[lang][FROM_TEXT]}: {wrap_tags(from_district_name, from_region_name)}',
        f'🏁 {PASSENGER_LAYOUT_DICT[lang][TO_TEXT]}: {wrap_tags(to_district_name, to_region_name)}\n',
        f'📞 {MAIL_LAYOUT_DICT[lang][RECEIVER_CONTACT_TEXT]}: {wrap_tags(receiver_contact)}',
        f'📦 {MAIL_LAYOUT_DICT[lang][MAIL_TEXT]}: {wrap_tags(comment)}\n',
        f'👤 {MAIL_LAYOUT_DICT[lang][SENDER_TEXT]}: {wrap_tags(fullname)}',
        f'📞 {PASSENGER_LAYOUT_DICT[lang][USER_PHONE_NUMBER_TEXT]}: {wrap_tags(phone_number)}\n',
        f'🤖 @{BOT_USERNAME} ©',
        f'🛡 cardel online ™',
    ]

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


def get_phone_number_layout(lang):
    """ Layout view
        telefon raqamini quyidagi formatda yuboring

        Misol: +998 XX xxx xx xx yoki XX xxx xx xx
    """
    return f"{PHONE_NUMBER_LAYOUT_DICT[lang][1]}:\n\n" \
           f"{PHONE_NUMBER_LAYOUT_DICT[lang][2]}: " \
           f"{wrap_tags('+998 XX xxx xx xx')} {PHONE_NUMBER_LAYOUT_DICT[lang][3]} {wrap_tags('XX xxx xx xx')}"
