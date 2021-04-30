import ujson
import datetime
import time

from telegram import TelegramError, ParseMode, InputFile
from telegram.ext import CallbackContext

from DB import *
from globalvariables import *
from languages import LANGS
from config import DEVELOPER_CHAT_ID, BOT_USERNAME


# from faker import Faker
# import random


def wrap_tags(*args):
    symbol = ' ' if len(args) > 1 else ''
    return f'<b><i><u>{symbol.join(args)}</u></i></b>'


def loop(icon, action, inline_keyboard):
    district_ids_list = []

    for row in inline_keyboard[1:]:
        for col in row:
            if col.callback_data != 'back':
                text = col.text.split(maxsplit=1)
                data = col.callback_data.split('_')
                col.text = f'{icon} {text[-1]}'
                col.callback_data = f'{data[0]}_{action}'
                district_ids_list.append(int(data[0]))

    return district_ids_list


def delete_message_by_message_id(context, user):
    user_data = context.user_data

    if MESSAGE_ID in user_data:
        try:
            context.bot.delete_message(user[TG_ID], user_data[MESSAGE_ID])
        except TelegramError:
            try:
                context.bot.edit_message_reply_markup(user[TG_ID], user_data[MESSAGE_ID])
            except TelegramError:
                pass
        finally:
            user_data.pop(MESSAGE_ID)


def set_data(user, driver_and_car_data, active_driver_data):
    data = dict()
    data[CHECKED] = dict()
    data[CHECKED]['from'] = ujson.loads(active_driver_data['from_'])
    data[CHECKED]['to'] = ujson.loads(active_driver_data['to_'])
    data[FULLNAME] = user[FULLNAME]
    data[PHONE_NUMBER] = user[PHONE_NUMBER]
    data[PHONE_NUMBER_2] = user[PHONE_NUMBER_2]
    data[CAR_MODEL] = driver_and_car_data[CAR_MODEL]
    data[BAGGAGE] = driver_and_car_data[BAGGAGE]
    data[EMPTY_SEATS] = active_driver_data[EMPTY_SEATS]
    data[ASK_PARCEL] = active_driver_data[ASK_PARCEL]
    data[COMMENT] = active_driver_data[COMMENT]
    departure_time = active_driver_data[DEPARTURE_TIME].split()
    data[DATE] = departure_time[0]
    data[TIME] = departure_time[-1]

    return data


def check_comment_length(comment):
    return True if len(comment) <= 255 else False


def get_text(lang, date_, time_):
    if lang == LANGS[0]:
        time_ = "noma'lum" if time_ == 'undefined' else time_
        text = "<b>Hurmatli haydovchi !\n" \
               f"Sizning aktiv holatingiz - [{date_}] [{time_}] da turibdi.\n" \
               "Aktiv holatingizni yangilab turishingizni so'raymiz. " \
               "Aktiv holatingizni yangilashingiz uchun siz:\n«🚕 Haydovchi» bo'limidan\n«✅ Aktiv holat» tugmasini " \
               "bosing va bu yerda siz \n«📝 Taxrirlash» tugmasi orqali vaqtni taxrirlashingiz yoki «❌ O'chirish» " \
               "tugmasini bosib qayta aktivlashtirishingiz mumkin.\n\nMurojaat uchun: @cardel_admin</b>"
    if lang == LANGS[1]:
        time_ = "неизвестно" if time_ == 'undefined' else time_
        text = "<b>Уважаемый водитель !\n" \
               f"Ваш активный статус - на [{date_}] [{time_}].\n" \
               "Пожалуйста, обновляйте свой активный статус. " \
               "Вы можете обновить свой активный статус:\nиз раздела «🚕 Bодитель» нажмите кнопку «✅ Активный статус» " \
               "и здесь вы можете редактировать время, используя кнопку «📝 Редактировать», или повторно " \
               "активировать его, нажимая кнопку «❌ Удалить».\n\nКонтакт: @cardel_admin</b>"
    if lang == LANGS[2]:
        time_ = "номаълум" if time_ == 'undefined' else time_
        text = "<b>Ҳурматли ҳайдовчи !\n" \
               f"Сизнинг актив ҳолатингиз - [{date_}] [{time_}] да турибди.\n" \
               "Актив ҳолатингизни янгилаб туришингизни сўраймиз. " \
               "Актив ҳолатингизни янгилашингиз учун сиз:\n«🚕 Ҳайдовчи» бўлимидан\n«✅ Актив ҳолат» тугмасини " \
               "босинг ва бу ерда сиз \n«📝 Тахрирлаш» тугмаси орқали вақтни тахрирлашингиз ёки «❌ Ўчириш» " \
               "тугмасини босиб кайта активлаштиришингиз мумкин.\n\nМурожаат учун: @cardel_admin</b>"

    return text


def filter_active_drivers(all_active_drivers):
    filtered_active_drivers = {}

    for active_driver in all_active_drivers:
        departure_time = active_driver[DEPARTURE_TIME].split()
        current_datetime = datetime.datetime.now()

        if departure_time[-1] == 'undefined':
            active_driver[DEPARTURE_TIME] = departure_time[0]
            date_string = '%d-%m-%Y'
            current_datetime = datetime.datetime(current_datetime.year, current_datetime.month, current_datetime.day)
        else:
            date_string = '%d-%m-%Y %H:%M'

        if current_datetime > datetime.datetime.strptime(active_driver[DEPARTURE_TIME], date_string):
            user = get_user(active_driver[USER_ID])
            active_driver_ = {
                USER_ID: active_driver[USER_ID],
                DRIVER_TEXT: get_text(user[LANG], date_=departure_time[0], time_=departure_time[-1])
            }
            filtered_active_drivers.update({user[TG_ID]: active_driver_})

    return filtered_active_drivers


def run_note_callback(context: CallbackContext):
    errors_list = []
    filtered_active_drivers = filter_active_drivers(get_all_active_drivers())

    start_time = datetime.datetime.now()
    for active_driver_tg_id, active_driver in filtered_active_drivers.items():
        try:
            context.bot.send_message(active_driver_tg_id, active_driver[DRIVER_TEXT], parse_mode=ParseMode.HTML)
            time.sleep(0.3)
        except TelegramError as e:
            errors_list.append(
                {'user_id': active_driver[USER_ID], 'user_tg_id': active_driver_tg_id, 'error_message': e.message}
            )
    end_time = datetime.datetime.now()

    errors_list.insert(0, {
        'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S.%f'),
        'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S.%f'),
        'delta': f'{(end_time - start_time).total_seconds()}s',
        'filtered_active_drivers_count': len(filtered_active_drivers),
        'errors_count': len(errors_list)
    })

    path = f'/var/www/html/{BOT_USERNAME}/logs/'
    document_name = datetime.datetime.now().strftime("daily_note_active_drivers_%d-%m-%Y_%H-%M-%S") + '.txt'
    full_path = path + document_name

    with open(full_path, 'w') as f:
        f.write(ujson.dumps(errors_list, indent=3))
    with open(full_path, 'r') as f:
        document = InputFile(f)
    context.bot.send_document(DEVELOPER_CHAT_ID, document=document)

# def fake_data_generator():
#     fake = Faker()
#     # for i in range(8, 401):
#     #     data = dict()
#     #     data[TG_ID] = i
#     #     data[FULLNAME] = fake.name()
#     #     data[PHONE_NUMBER] = '+998' + str(random.randint(1000000, 9999999))
#     #     data[IS_ADMIN] = random.randint(0, 1)
#     #     data[LANG] = random.choice(LANGS)
#     #
#     #     insert_data(data, 'users')
#     # exit()
#
#     # for i in range(201, 401):
#     #     data = dict()
#     #     data[USER_ID] = i
#     #     data[STATUS] = 'standart'
#     #     data[CAR_ID] = random.randint(1, 10)
#     #     data[BAGGAGE] = random.randint(0, 1)
#     #
#     #     insert_data(data, 'drivers')
#     # exit()
#
#     for i in range(1, 100):
#         data = dict()
#         data[DRIVER_ID] = data[USER_ID] = i
#         data[EMPTY_SEATS] = random.randint(1, 4)
#         data[ASK_PARCEL] = random.randint(0, 1)
#         data[DEPARTURE_TIME] = f'{random.randint(10, 28)}-0{random.randint(1, 4)}-2021 ' \
#                                f'{random.choice(["undefined", f"{random.randint(10, 23)}:00"])}'
#         region_id = random.choice([1, 19, 33, 47, 63, 74, 87, 104, 119, 132, 144, 167, 187, 201])
#         data['from_'] = {region_id: [x for x in range(region_id + 1, region_id + 11)]}
#         data['from_'] = ujson.dumps(data['from_'])
#         region_id = random.choice([1, 19, 33, 47, 63, 74, 87, 104, 119, 132, 144, 167, 187, 201])
#         data['to_'] = {region_id: [x for x in range(region_id + 1, region_id + 11)]}
#         data['to_'] = ujson.dumps(data['to_'])
#
#         insert_data(data, 'active_drivers')
#
#     exit()
