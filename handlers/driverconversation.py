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
from DB import insert_data, get_user, get_driver
from languages import LANGS
from layouts import get_passenger_layout, get_phone_number_layout, get_parcel_layout
from globalvariables import *
from helpers import wrap_tags
from filters import phone_number_filter

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *
from replykeyboards.replykeyboardtypes import reply_keyboard_types

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *

import logging
import datetime
import re

logger = logging.getLogger()


def driver_conversation_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    driver = get_driver(user[ID])

    if driver is None:

        if user[LANG] == LANGS[0]:
            text = "Haydochi sifatida ro'yxatdan o'tmoqchimisiz"
        if user[LANG] == LANGS[1]:
            text = "Вы хотите зарегистрироваться как водител"
        if user[LANG] == LANGS[2]:
            text = "Ҳайдочи сифатида рўйхатдан ўтмоқчимисиз"

        update.message.reply_text(update.message.text, reply_markup=ReplyKeyboardRemove())
        text = f'🟡 {text}?'
        inline_keyboard = InlineKeyboard(yes_no_keyboard, user[LANG]).get_keyboard()
        message = update.message.reply_text(text, reply_markup=inline_keyboard)

        state = YES_NO
        user_data[STATE] = state
        user_data[MESSAGE_ID] = message.message_id

    else:
        reply_keyboard = ReplyKeyboard(driver_keyboard, user[LANG]).get_keyboard()
        update.message.reply_text(update.message.text, reply_markup=reply_keyboard)

        sate = ConversationHandler.END

    logger.info('user_data: %s', user_data)
    return sate


def yes_no_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data

    if data == 'no':

        try:
            callback_query.delete_message()
        except TelegramError:
            callback_query.edit_message_reply_markup()

        icon = reply_keyboard_types[passenger_parcel_keyboard][5]['icon']
        text = reply_keyboard_types[passenger_parcel_keyboard][5][f'text_{user[LANG]}']
        text = f'{icon} {text}'
        reply_keyboard = ReplyKeyboard(main_menu_keyboard, user[LANG]).get_keyboard()
        callback_query.message.reply_text(text, reply_markup=reply_keyboard)

        user_data.clear()
        state = ConversationHandler.END

    elif data == 'yes':
        if user[LANG] == LANGS[0]:
            text = "Avtomabilingiz rusumini tanlang"
        if user[LANG] == LANGS[1]:
            text = "Выберите модель вашего автомобиля"
        if user[LANG] == LANGS[2]:
            text = "Автомабилингиз русумини танланг"

        text = f'🚕 {text}:'
        inline_keyboard = InlineKeyboard(car_models_keyboard).get_keyboard()
        callback_query.edit_message_text(text, reply_markup=inline_keyboard)

        state = CAR_MODEL
        user_data[STATE] = state

    logger.info('user_data: %s', user_data)
    return state


def car_model_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query

    user_data[CAR_ID] = callback_query.data

    if user[LANG] == LANGS[0]:
        text = "Bagaj(yuqori bagaj) bormi"
    if user[LANG] == LANGS[1]:
        text = "Есть ли багаж (верхний багаж)"
    if user[LANG] == LANGS[2]:
        text = "Багаж(юқори багаж) борми"

    text = f'{text}?'
    inline_keyboard = InlineKeyboard(yes_no_keyboard, user[LANG]).get_keyboard()
    callback_query.edit_message_text(text, reply_markup=inline_keyboard)

    user_data[STATE] = BAGGAGE

    logger.info('user_data: %s', user_data)
    return BAGGAGE


def baggage_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = dict()

    data[BAGGAGE] = True if callback_query.data == 'yes' else False
    data[USER_ID] = user[ID]
    data[STATUS] = 'standart'
    data[CAR_ID] = user_data[CAR_ID]

    # Inset driver data to database
    # insert_data(data, 'drivers')

    if user[LANG] == LANGS[0]:
        text = "Registratsiya muvofaqqiyatli yakunlandi"
        text_2 = "Haydovchi"
    if user[LANG] == LANGS[1]:
        text = "Регистрация успешно завершена"
        text_2 = "Водитель"
    if user[LANG] == LANGS[2]:
        text = "Регистрация мувофаққиятли якунланди"
        text_2 = "Ҳайдовчи"

    text = f'{text}! 👍'
    callback_query.edit_message_text(text)

    text_2 = f'🚕 {text_2}'
    reply_keyboard = ReplyKeyboard(driver_keyboard, user[LANG]).get_keyboard()
    callback_query.message.reply_text(text_2, reply_markup=reply_keyboard)

    user_data.clear()
    return ConversationHandler.END


def driver_fallback(update: Update, context: CallbackContext):
    print('driver fallback')


driver_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(r"(Haydovchi|Водитель|Ҳайдовчи)$") &
                                 (~Filters.update.edited_message), driver_conversation_callback)],

    states={
        YES_NO: [CallbackQueryHandler(yes_no_callback, pattern=r'^(yes|no)$')],

        CAR_MODEL: [CallbackQueryHandler(car_model_callback, pattern=r'^\d+$')],

        BAGGAGE: [CallbackQueryHandler(baggage_callback, pattern=r'^(yes|no)$')],

    },
    fallbacks=[
        MessageHandler(Filters.text & (~Filters.update.edited_message), driver_fallback)
    ],

    persistent=True,

    name='driver_conversation'
)
