from telegram import (
    Update,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
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
from DB import insert_data, get_user, get_driver_and_car_data, get_active_drivers_by_seats
from languages import LANGS
from layouts import get_active_driver_layout, get_comment_text
from globalvariables import *
from helpers import wrap_tags

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *
from inlinekeyboards.inlinekeyboardtypes import inline_keyboard_types

import logging
import datetime
import json
import random

logger = logging.getLogger()


def search_conversation_callback(update: Update, context: CallbackContext):
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

    logger.info('user_data: %s', user_data)
    return DISTRICT


def district_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data
    callback_query.answer()

    if data == 'back' or user_data[STATE] == FROM_DISTRICT:

        if user[LANG] == LANGS[0]:
            text = "Qayerdan"
            text_2 = "Qayerga"
            text_3 = "(Viloyatni tanlang)"

        if user[LANG] == LANGS[1]:
            text = "Откуда"
            text_2 = "Куда"
            text_3 = "(Выберите область)"

        if user[LANG] == LANGS[2]:
            text = "Қаердан"
            text_2 = "Қаерга"
            text_3 = "(Вилоятни танланг)"

        if data == 'back':
            if user_data[STATE] == FROM_DISTRICT:
                state = FROM_REGION
            elif user_data[STATE] == TO_DISTRICT:
                text = text_2
                state = TO_REGION
            user_data.pop(state)

        else:
            text = text_2
            state = TO_REGION
            user_data[user_data[STATE]] = int(data)

        text = f'{text} {text_3}:'
        inline_keyboard = InlineKeyboard(regions_keyboard, user[LANG]).get_keyboard()
        callback_query.edit_message_text(text, reply_markup=inline_keyboard)

        user_data[STATE] = state

        logger.info('user_data: %s', user_data)
        return REGION

    elif user_data[STATE] == TO_DISTRICT:

        user_data[user_data[STATE]] = int(data)

        if user[LANG] == LANGS[0]:
            text = "Yo'lovchi sonini belgilang"

        if user[LANG] == LANGS[1]:
            text = "Укажите количество пассажиров"

        if user[LANG] == LANGS[2]:
            text = "Йўловчи сонини белгиланг"

        text = f'{text}:'
        inline_keyboard = callback_query.message.reply_markup.from_row([
            InlineKeyboardButton('1', callback_data='1'),
            InlineKeyboardButton('2', callback_data='2'),
            InlineKeyboardButton('3', callback_data='3'),
            InlineKeyboardButton('4', callback_data='4'),
        ])

        user_data[STATE] = EMPTY_SEATS
        callback_query.edit_message_text(text, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)

        logger.info('user_data: %s', user_data)
        return EMPTY_SEATS


def empty_seats_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data
    callback_query.answer()
    user_data[EMPTY_SEATS] = int(data)
    search_from_region = user_data[FROM_REGION]
    search_from_district = user_data[FROM_DISTRICT]
    search_to_region = user_data[TO_REGION]
    search_to_district = user_data[TO_DISTRICT]
    active_drivers = get_active_drivers_by_seats(user_data[EMPTY_SEATS])
    # print(active_drivers)
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

    print(found_active_drivers)

    logger.info('user_data: %s', user_data)


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
    entry_points=[MessageHandler(Filters.regex(r"(Taksi qidirsh|Поиск такси|Такси қидирш)$") &
                                 (~Filters.update.edited_message), search_conversation_callback)],

    states={
        REGION: [CallbackQueryHandler(region_callback, pattern=r'^\d+$')],

        DISTRICT: [CallbackQueryHandler(district_callback, pattern=r'^(back|\d+)$')],

        EMPTY_SEATS: [CallbackQueryHandler(empty_seats_callback, pattern=r'^\d+$')],

        # CONFIRMATION: [CallbackQueryHandler(confirmation_callback, pattern='^(confirm|cancel)$')]
    },
    fallbacks=[MessageHandler(Filters.text & (~Filters.update.edited_message), search_fallback)],

    persistent=True,

    name='search_conversation'
)
