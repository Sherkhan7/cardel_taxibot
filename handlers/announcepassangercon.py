from telegram import Update, ReplyKeyboardRemove, InlineKeyboardButton, ParseMode
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    Filters
)

from config import ACTIVE_ADMINS
from DB import insert_data, get_user
from languages import LANGS
from layouts import get_passenger_layout
from globalvariables import *

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *

import logging
import datetime

logger = logging.getLogger()


def announce_passenger_callback(update: Update, context: CallbackContext):
    # with open('jsons/update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    if user[LANG] == LANGS[0]:
        text = "Qayerdan (Viloyatni tanlang)"

    if user[LANG] == LANGS[1]:
        text = "Откуда (Выберите область)"

    if user[LANG] == LANGS[2]:
        text = "Қаердан (Вилоятни танланг)"

    update.message.reply_text(update.message.text, reply_markup=ReplyKeyboardRemove())

    text = f'{text} :'
    inline_keyboard = InlineKeyboard(regions_keyboard, user[LANG]).get_keyboard()
    message = update.message.reply_text(text, reply_markup=inline_keyboard)

    state = FROM_REGION
    user_data[STATE] = state
    user_data[MESSAGE_ID] = message.message_id

    return REGION


def region_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    region_id = callback_query.data
    user_data[user_data[STATE]] = int(region_id)

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

        text = f'{text} :'
        inline_keyboard = callback_query.message.reply_markup.from_row([
            InlineKeyboardButton('1', callback_data='1'),
            InlineKeyboardButton('2', callback_data='2'),
            InlineKeyboardButton('3', callback_data='3'),
            InlineKeyboardButton('4', callback_data='4'),
        ])
        callback_query.edit_message_text(text, reply_markup=inline_keyboard)

        user_data[STATE] = PASSENGERS

        logger.info('user_data: %s', user_data)
        return PASSENGERS


def passenger_quantity_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    callback_query.answer()

    user_data[PASSENGERS] = int(callback_query.data)

    if user[LANG] == LANGS[0]:
        text = "Ketish kunini belgilang"

    if user[LANG] == LANGS[1]:
        text = "Установите дату отъезда"

    if user[LANG] == LANGS[2]:
        text = "Кетиш кунини белгиланг"

    text = f'{text} :'
    inline_keyboard = InlineKeyboard(dates_keyboard, user[LANG]).get_keyboard()
    callback_query.edit_message_text(text, reply_markup=inline_keyboard)

    user_data[STATE] = DATE

    logger.info('user_data: %s', user_data)
    return DATE


def date_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data
    callback_query.answer()

    if data == 'now':

        user_data[DATE] = datetime.datetime.now().strftime('%d-%m-%Y')
        user_data[TIME] = 'now'

        if user[LANG] == LANGS[0]:
            text = "Agar izohlaringiz bo'lsa yozib yuboring"
            button_text = "Izoh yo'q"

        if user[LANG] == LANGS[1]:
            text = "Если у вас есть какие-либо комментарии, пожалуйста, напишите"
            button_text = "Нет комментариев"

        if user[LANG] == LANGS[2]:
            text = "Агар изоҳларингиз бўлса ёзиб юборинг"
            button_text = "Изоҳ йўқ"

        text = f'{text} :'
        inline_keyboard = callback_query.message.reply_markup
        inline_keyboard.from_button(InlineKeyboardButton(button_text, callback_data='no_comment'))
        callback_query.edit_message_text(text, reply_markup=inline_keyboard)

        state = COMMENT

    else:

        user_data[DATE] = data

        if user[LANG] == LANGS[0]:
            text = "Soatni belgilang"

        if user[LANG] == LANGS[1]:
            text = "Выберите время"

        if user[LANG] == LANGS[2]:
            text = "Соатни белгиланг"

        text = f'{text} :'
        inline_keyboard = InlineKeyboard(times_keyboard, user[LANG], data={'begin': 6, 'end': 17}).get_keyboard()
        callback_query.edit_message_text(text, reply_markup=inline_keyboard)

        state = TIME

    user_data[STATE] = state

    logger.info('user_data: %s', user_data)
    return state


def time_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data
    callback_query.answer()

    if data == 'next' or data == 'back':

        if data == 'next':
            inline_keyboard = InlineKeyboard(times_keyboard, user[LANG], data={'begin': 18, 'end': 29}).get_keyboard()
        if data == 'back':
            inline_keyboard = InlineKeyboard(times_keyboard, user[LANG], data={'begin': 6, 'end': 17}).get_keyboard()

        callback_query.edit_message_reply_markup(inline_keyboard)

        state = TIME

    else:

        user_data[TIME] = data

        if user[LANG] == LANGS[0]:
            text = "Agar izohlaringiz bo'lsa yozib yuboring"
            button_text = "Izoh yo'q"

        if user[LANG] == LANGS[1]:
            text = "Если у вас есть какие-либо комментарии, пожалуйста, напишите"
            button_text = "Нет комментариев"

        if user[LANG] == LANGS[2]:
            text = "Агар изоҳларингиз бўлса ёзиб юборинг"
            button_text = "Изоҳ йўқ"

        text = f'{text} :'
        inline_keyboard = callback_query.message.reply_markup
        inline_keyboard = inline_keyboard.from_button(InlineKeyboardButton(button_text, callback_data='no_comment'))
        callback_query.edit_message_text(text, reply_markup=inline_keyboard)

        state = COMMENT

    user_data[STATE] = state

    logger.info('user_data: %s', user_data)
    return state


def comment_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    user_data[FULLNAME] = user[FULLNAME]
    user_data[PHONE_NUMBER] = user[PHONE_NUMBER]
    inline_keyboard = InlineKeyboard(confirm_keyboard, user[LANG]).get_keyboard()

    if callback_query is None:
        user_data[COMMENT] = update.message.text
        context.bot.delete_message(update.effective_user.id, user_data[MESSAGE_ID])

        layout = get_passenger_layout(user[LANG], data=user_data)
        message = update.message.reply_html(layout, reply_markup=inline_keyboard)
        user_data[MESSAGE_ID] = message.message_id

    else:
        user_data[COMMENT] = None
        layout = get_passenger_layout(user[LANG], data=user_data)
        callback_query.edit_message_text(layout, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)

    user_data[STATE] = CONFIRMATION

    logger.info('user_data: %s', user_data)
    return CONFIRMATION


def confirmation_callback(update: Update, context: CallbackContext):
    pass


def announce_passenger_fallback(update: Update, context: CallbackContext):
    print('announce_passenger_fallback')


announce_passenger_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(r"(Yo'lovchi e'lon berish|Пассажир объявление|Йўловчи эълон бериш)$") &
                                 (~Filters.update.edited_message), announce_passenger_callback)],

    states={
        REGION: [CallbackQueryHandler(region_callback, pattern=r'^(\d+)$')],

        DISTRICT: [CallbackQueryHandler(district_callback, pattern=r'^(\d+|back)$')],

        PASSENGERS: [CallbackQueryHandler(passenger_quantity_callback, pattern=r'^(\d+)$')],

        DATE: [CallbackQueryHandler(date_callback, pattern=r'^(now|\d+[-]\d+[-]\d+)$')],

        TIME: [CallbackQueryHandler(time_callback, pattern=r'^(back|next|\d+[:]00)$')],

        COMMENT: [
            CallbackQueryHandler(comment_callback, pattern=r'^no_comment$'),
            MessageHandler(Filters.text & (~Filters.command) & (~Filters.update.edited_message),
                           comment_callback)
        ],

        CONFIRMATION: [CallbackQueryHandler(confirmation_callback, pattern='^(confirm)$')]
    },
    fallbacks=[
        CommandHandler(['start', 'menu', 'cancel'], announce_passenger_fallback),
        MessageHandler(Filters.text, announce_passenger_fallback)
    ],

    persistent=True,

    name='announce_passenger_conversation'
)
