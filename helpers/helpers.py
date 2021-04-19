import ujson

from telegram import TelegramError
from globalvariables import *


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
    data[CAR_MODEL] = driver_and_car_data[CAR_MODEL]
    data[BAGGAGE] = driver_and_car_data[BAGGAGE]
    data[EMPTY_SEATS] = active_driver_data[EMPTY_SEATS]
    data[ASK_PARCEL] = active_driver_data[ASK_PARCEL]
    data[COMMENT] = active_driver_data[COMMENT]
    departure_time = active_driver_data[DEPARTURE_TIME].split()
    data[DATE] = departure_time[0]
    data[TIME] = departure_time[-1]

    return data

# def fake_data_generator():
#     fake = Faker()
#     for i in range(8, 401):
#         data = dict()
#         data[TG_ID] = i
#         data[FULLNAME] = fake.name()
#         data[PHONE_NUMBER] = '+998' + str(random.randint(1000000, 9999999))
#         data[IS_ADMIN] = random.randint(0, 1)
#         data[LANG] = random.choice(LANGS)
#
#         insert_data(data, 'users')
#     exit()
#
#     for i in range(201, 401):
#         data = dict()
#         data[USER_ID] = i
#         data[STATUS] = 'standart'
#         data[CAR_ID] = random.randint(1, 10)
#         data[BAGGAGE] = random.randint(0, 1)
#
#         insert_data(data, 'drivers')
#     exit()
#
#     for i in range(1, 401):
#         data = dict()
#         data[DRIVER_ID] = i
#         data[EMPTY_SEATS] = random.randint(1, 4)
#         data[ASK_PARCEL] = random.randint(0, 1)
#         data[DEPARTURE_TIME] = datetime.datetime.now()
#         region_id = random.choice([1, 19, 33, 47, 63, 74, 87, 104, 119, 132, 144, 167, 187, 201])
#         data['from_'] = {region_id: [x for x in range(region_id + 1, region_id + 11)]}
#         data['from_'] = json.dumps(data['from_'])
#         region_id = random.choice([1, 19, 33, 47, 63, 74, 87, 104, 119, 132, 144, 167, 187, 201])
#         data['to_'] = {region_id: [x for x in range(region_id + 1, region_id + 11)]}
#         data['to_'] = json.dumps(data['to_'])
#
#         insert_data(data, 'active_drivers')
#
#     exit()
