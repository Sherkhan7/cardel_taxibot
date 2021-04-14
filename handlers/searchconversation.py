from telegram import (
    Update,
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ParseMode,
    TelegramError,
)
from telegram.ext import (
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    Filters,
)
from DB import *
from languages import LANGS
from layouts import get_active_driver_layout
from globalvariables import *
from helpers import wrap_tags

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *

import logging
import json
import re
# import random
# from faker import Faker

logger = logging.getLogger()


def search_conversation_callback(update: Update, context: CallbackContext):
    # fake = Faker()
    # for i in range(8, 401):
    #     data = dict()
    #     data[TG_ID] = i
    #     data[FULLNAME] = fake.name()
    #     data[PHONE_NUMBER] = '+998' + str(random.randint(1000000, 9999999))
    #     data[IS_ADMIN] = random.randint(0, 1)
    #     data[LANG] = random.choice(LANGS)
    #
    #     insert_data(data, 'users')
    # exit()

    # for i in range(201, 401):
    #     data = dict()
    #     data[USER_ID] = i
    #     data[STATUS] = 'standart'
    #     data[CAR_ID] = random.randint(1, 10)
    #     data[BAGGAGE] = random.randint(0, 1)
    #
    #     insert_data(data, 'drivers')
    # exit()

    # for i in range(1, 401):
    #     data = dict()
    #     data[DRIVER_ID] = i
    #     data[EMPTY_SEATS] = random.randint(1, 4)
    #     data[ASK_PARCEL] = random.randint(0, 1)
    #     data[DEPARTURE_TIME] = datetime.datetime.now()
    #     region_id = random.choice([1, 19, 33, 47, 63, 74, 87, 104, 119, 132, 144, 167, 187, 201])
    #     data['from_'] = {region_id: [x for x in range(region_id + 1, region_id + 11)]}
    #     data['from_'] = json.dumps(data['from_'])
    #     region_id = random.choice([1, 19, 33, 47, 63, 74, 87, 104, 119, 132, 144, 167, 187, 201])
    #     data['to_'] = {region_id: [x for x in range(region_id + 1, region_id + 11)]}
    #     data['to_'] = json.dumps(data['to_'])
    #
    #     insert_data(data, 'active_drivers')
    #
    # exit()

    user = get_user(update.effective_user.id)
    user_data = context.user_data
    text = update.message.text

    if user[LANG] == LANGS[0]:
        text = "Qayerdan (Viloyatni tanlang)"

    if user[LANG] == LANGS[1]:
        text = "Откуда (Выберите область)"

    if user[LANG] == LANGS[2]:
        text = "Қаердан (Вилоятни танланг)"

    update.message.reply_text(update.message.text, reply_markup=ReplyKeyboardRemove())

    text = f'{text}:'
    inline_keyboard = InlineKeyboard(regions_keyboard, user[LANG]).get_keyboard()
    message = update.message.reply_text(text, reply_markup=inline_keyboard)

    user_data[STATE] = FROM_REGION
    user_data[MESSAGE_ID] = message.message_id

    return REGION


def region_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    region_id = callback_query.data
    user_data[user_data[STATE]] = str(region_id)

    if user[LANG] == LANGS[0]:
        text = "Qayerdan"
        text_2 = "Qayerga"
        text_3 = "(Tumanni tanlang)"

    if user[LANG] == LANGS[1]:
        text = "Откуда"
        text_2 = "Куда"
        text_3 = "(Выберите район)"

    if user[LANG] == LANGS[2]:
        text = "Қаердан"
        text_2 = "Қаерга"
        text_3 = "(Туманни танланг)"

    if user_data[STATE] == FROM_REGION:
        state = FROM_DISTRICT
    elif user_data[STATE] == TO_REGION:
        text = text_2
        state = TO_DISTRICT

    text = f'{text} {text_3}:'
    inline_keyboard = InlineKeyboard(districts_keyboard, user[LANG], data=region_id).get_keyboard()

    callback_query.answer()
    callback_query.edit_message_text(text, reply_markup=inline_keyboard)

    user_data[STATE] = state

    # logger.info('user_data: %s', user_data)
    return DISTRICT


def district_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data
    callback_query.answer()

    if user[LANG] == LANGS[0]:
        from_text = "Qayerdan"
        to_text = "Qayerga"
        region_text = "(Viloyatni tanlang)"
        stop_btn = "Qidiruvni to'xtatish"
        set_seats_text = "Yo'lovchi sonini belgilang"

    if user[LANG] == LANGS[1]:
        from_text = "Откуда"
        to_text = "Куда"
        region_text = "(Выберите область)"
        stop_btn = "Остановить поиск"
        set_seats_text = "Укажите количество пассажиров"

    if user[LANG] == LANGS[2]:
        from_text = "Қаердан"
        to_text = "Қаерга"
        region_text = "(Вилоятни танланг)"
        stop_btn = "Қидирувни тўхтатиш"
        set_seats_text = "Йўловчи сонини белгиланг"

    if data == 'back' or user_data[STATE] == FROM_DISTRICT:

        if data == 'back':
            if user_data[STATE] == FROM_DISTRICT:
                state = FROM_REGION
            elif user_data[STATE] == TO_DISTRICT:
                from_text = to_text
                state = TO_REGION
            user_data.pop(state)

        else:
            from_text = to_text
            state = TO_REGION
            user_data[user_data[STATE]] = int(data)

        from_text = f'{from_text} {region_text}:'
        inline_keyboard = InlineKeyboard(regions_keyboard, user[LANG]).get_keyboard()
        callback_query.edit_message_text(from_text, reply_markup=inline_keyboard)

        user_data[STATE] = state

        # logger.info('user_data: %s', user_data)
        return REGION

    elif user_data[STATE] == TO_DISTRICT:

        user_data[user_data[STATE]] = int(data)

        reply_keyboard = ReplyKeyboardMarkup([
            [
                KeyboardButton('1'),
                KeyboardButton('2'),
                KeyboardButton('3'),
                KeyboardButton('4'),
            ],
            [KeyboardButton(f'🔍 {stop_btn}')]
        ], resize_keyboard=True)
        from_point = get_region_and_district(user_data[FROM_REGION], user_data[FROM_DISTRICT])
        from_region_name = from_point[0][f'name_{user[LANG]}']
        from_district_name = from_point[1][f'name_{user[LANG]}']

        to_point = get_region_and_district(user_data[TO_REGION], user_data[TO_DISTRICT])
        to_region_name = to_point[0][f'name_{user[LANG]}']
        to_district_name = to_point[1][f'name_{user[LANG]}']

        edit_text = f"{from_text}: {wrap_tags(from_region_name, from_district_name)}\n\n" \
                    f"{to_text}: {wrap_tags(to_region_name, to_district_name)}"
        callback_query.edit_message_text(edit_text, parse_mode=ParseMode.HTML)

        callback_query.message.reply_text(set_seats_text, reply_markup=reply_keyboard)

        user_data[STATE] = EMPTY_SEATS
        user_data.pop(MESSAGE_ID)

        # logger.info('user_data: %s', user_data)
        return EMPTY_SEATS


def empty_seats_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    not_found_icon = "🙊"
    text = update.message.text

    stop_search = re.search("(Qidiruvni to'xtatish|Остановить поиск|Қидирувни тўхтатиш)$", text)

    if user[LANG] == LANGS[0]:
        not_found_text = "Kechirasiz, birortaham taksi topilmadi"
        found_text = "Barcha topilgan taksilar soni"
        stop_search_text = "Qidiruv to'xtatildi"
    if user[LANG] == LANGS[1]:
        not_found_text = "К сожалению, не было найдено ни одного такси"
        found_text = "Всего найдено такси"
        stop_search_text = "Поиск был остановлен"
    if user[LANG] == LANGS[2]:
        not_found_text = "Кечирасиз, бирортаҳам такси топилмади"
        found_text = "Барча топилган таксилар сони"
        stop_search_text = "Қидирув тўхтатилди"

    if stop_search:
        stop_search_text = f'‼ {stop_search_text}!'
        reply_keyboard = ReplyKeyboard(main_menu_keyboard, user[LANG]).get_keyboard()
        update.message.reply_text(stop_search_text, reply_markup=reply_keyboard)
        user_data.clear()
        return ConversationHandler.END

    user_data[EMPTY_SEATS] = int(text)
    search_from_region = user_data[FROM_REGION]
    search_from_district = user_data[FROM_DISTRICT]
    search_to_region = user_data[TO_REGION]
    search_to_district = user_data[TO_DISTRICT]
    empty_seats_list = [i for i in range(user_data[EMPTY_SEATS], 5)]
    active_drivers = get_active_drivers_by_seats(empty_seats_list)
    found_active_drivers = []

    for active_driver in active_drivers:
        from_ = json.loads(active_driver['from_'])
        to_ = json.loads(active_driver['to_'])
        found_from_region = search_from_region in from_
        found_to_region = search_to_region in to_

        if found_from_region and found_to_region:
            found_from_district = search_from_district in from_[search_from_region]
            found_to_district = search_to_district in to_[search_to_region]

            if found_to_district and found_from_district:
                found_active_drivers.append(active_driver)

    # logger.info('user_data: %s', user_data)
    if not found_active_drivers:
        update.message.reply_text(f'{not_found_icon} {not_found_text}')

        data = dict()
        data[USER_ID] = user[ID]
        data[FROM_REGION] = user_data[FROM_REGION]
        data[FROM_DISTRICT] = user_data[FROM_DISTRICT]
        data[TO_REGION] = user_data[TO_REGION]
        data[TO_DISTRICT] = user_data[TO_DISTRICT]
        data[EMPTY_SEATS] = user_data[EMPTY_SEATS]

        insert_data(data, 'search_history')

        return

    else:
        for found_active_driver in found_active_drivers:
            driver = get_driver_by_driver_id(found_active_driver[DRIVER_ID])
            driver_user_data = get_user(driver[USER_ID])
            data = dict()
            data[CHECKED] = dict()
            data[FULLNAME] = driver_user_data[FULLNAME]
            data[PHONE_NUMBER] = driver_user_data[PHONE_NUMBER]
            data[CAR_MODEL] = get_driver_and_car_data(driver[USER_ID])[CAR_MODEL]
            data[BAGGAGE] = driver[BAGGAGE]
            data[CHECKED]['from'] = json.loads(found_active_driver['from_'])
            data[CHECKED]['to'] = json.loads(found_active_driver['to_'])
            data[EMPTY_SEATS] = found_active_driver[EMPTY_SEATS]
            data[ASK_PARCEL] = found_active_driver[ASK_PARCEL]
            data[COMMENT] = found_active_driver[COMMENT]
            departure_time = found_active_driver[DEPARTURE_TIME].split()
            data[DATE] = departure_time[0]
            data[TIME] = departure_time[-1]
            layout = get_active_driver_layout(user[LANG], data=data)
            update.message.reply_html(layout)

        update.message.reply_text(f'{found_text}: {len(found_active_drivers)}')
        return


def search_fallback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    text = update.message.text

    if text == '/start' or text == '/menu' or text == '/cancel':

        if user[LANG] == LANGS[0]:
            text = "Qidruv bekor qilindi"
        if user[LANG] == LANGS[1]:
            text = "Поиск отменено"
        if user[LANG] == LANGS[2]:
            text = "Қидирув бекор қилинди"

        text = f'‼ {text} !'
        reply_keyboard = ReplyKeyboard(main_menu_keyboard, user[LANG]).get_keyboard()
        update.message.reply_text(text, reply_markup=reply_keyboard)

        if MESSAGE_ID in user_data:
            try:
                context.bot.delete_message(user[TG_ID], user_data[MESSAGE_ID])
            except TelegramError:
                try:
                    context.bot.edit_message_reply_markup(user[TG_ID], user_data[MESSAGE_ID])
                except TelegramError:
                    pass

        user_data.clear()
        return ConversationHandler.END

    else:

        if user[LANG] == LANGS[0]:
            text = "Hozir siz taksi qidirish bo'limidasiz.\n\n" \
                   "Qidiruvni to'xtatish uchun /cancel ni bosing."
        if user[LANG] == LANGS[1]:
            text = "Сейчас вы находитесь в разделе поиска такси.\n\n" \
                   "Нажмите /cancel, чтобы остановить поиск."
        if user[LANG] == LANGS[2]:
            text = "Ҳозир сиз такси қидириш бўлимидасиз.\n\n" \
                   "Қидирувни тўхтатиш учун /cancel ни босинг."

        update.message.reply_text(text)
        return


search_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(r"(Taksi qidirish|Поиск такси|Такси қидириш)$") &
                                 (~Filters.update.edited_message), search_conversation_callback)],

    states={
        REGION: [CallbackQueryHandler(region_callback, pattern=r'^\d+$')],

        DISTRICT: [CallbackQueryHandler(district_callback, pattern=r'^(back|\d+)$')],

        EMPTY_SEATS: [
            MessageHandler(Filters.regex("([1-4])|(Qidiruvni to'xtatish|Остановить поиск|Қидирувни тўхтатиш)"),
                           empty_seats_callback)],

    },
    fallbacks=[MessageHandler(Filters.text & (~Filters.update.edited_message), search_fallback)],

    persistent=True,

    name='search_conversation'
)
