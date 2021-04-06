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
from layouts import *
from DB import insert_data, get_user
from languages import LANGS
from globalvariables import *
from helpers import wrap_tags
from filters import phone_number_filter

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *

import logging
import datetime
import re

logger = logging.getLogger()


def announce_conversation_callback(update: Update, context: CallbackContext):
    # with open('jsons/update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    text = update.message.text
    announce_passenger = re.search(r"(Yo'lovchi e'lon berish|Пассажир объявление|Йўловчи эълон бериш)$", text)
    announce_parcel = re.search(r"(Pochta e'lon berish|Почта объявление|Почта эълон бериш)$", text)

    user_data[ANNOUNCE] = PARCEL if announce_parcel else PASSENGER if announce_passenger else None

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
            text_2 = "Pochta qabul qiluvchining telefon raqamini yuboring"

        if user[LANG] == LANGS[1]:
            text = "Укажите количество пассажиров"
            text_2 = "Отправьте номер телефона получателя почты"

        if user[LANG] == LANGS[2]:
            text = "Йўловчи сонини белгиланг"
            text_2 = "Почта қабул қилувчининг телефон рақамини юборинг"

        text = f'{text}:'
        inline_keyboard = callback_query.message.reply_markup.from_row([
            InlineKeyboardButton('1', callback_data='1'),
            InlineKeyboardButton('2', callback_data='2'),
            InlineKeyboardButton('3', callback_data='3'),
            InlineKeyboardButton('4', callback_data='4'),
        ])
        state = PASSENGERS

        if user_data[ANNOUNCE] == PARCEL:
            text = text_2
            layout = get_phone_number_layout(user[LANG])
            text += f'.\n\n{layout}'
            state = RECEIVER_CONTACT
            inline_keyboard = None

        user_data[STATE] = state
        callback_query.edit_message_text(text, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)

        logger.info('user_data: %s', user_data)
        return state


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

    text = f'{text}:'
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

        text = get_comment_text(user[LANG])
        inline_keyboard = callback_query.message.reply_markup
        inline_keyboard = inline_keyboard.from_button(InlineKeyboardButton(text[1], callback_data='no_comment'))
        callback_query.edit_message_text(text[0], reply_markup=inline_keyboard)

        state = COMMENT

    else:

        user_data[DATE] = data

        if user[LANG] == LANGS[0]:
            text = "Soatni belgilang"

        if user[LANG] == LANGS[1]:
            text = "Выберите время"

        if user[LANG] == LANGS[2]:
            text = "Соатни белгиланг"

        text = f'{text}:'
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

        text = get_comment_text(user[LANG])
        inline_keyboard = callback_query.message.reply_markup
        inline_keyboard = inline_keyboard.from_button(InlineKeyboardButton(text[1], callback_data='no_comment'))
        callback_query.edit_message_text(text[0], reply_markup=inline_keyboard)

        state = COMMENT

    user_data[STATE] = state

    logger.info('user_data: %s', user_data)
    return state


def receiver_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    phone_number = update.message.contact.phone_number if update.message.contact else update.message.text
    phone_number = phone_number_filter(phone_number)

    if not phone_number:

        error_text = get_phone_number_error_text(user[LANG])
        layout = get_phone_number_layout(user[LANG])
        error_text = f'❌ {error_text}!\n\n' + layout
        update.message.reply_html(error_text, quote=True)
        state = user_data[STATE]

    else:

        user_data[RECEIVER_CONTACT] = phone_number

        if user[LANG] == LANGS[0]:
            text = "Pochta haqida izoh yuboring:\n\n" \
                   f"{wrap_tags('Misol uchun: sumka, hujjat, yuk')}"

        if user[LANG] == LANGS[1]:
            text = "Отправить комментарий о почте:\n\n" \
                   f"{wrap_tags('Например: сумка, документ, посылка')}"

        if user[LANG] == LANGS[2]:
            text = "Почта ҳақида изоҳ юборинг:\n\n" \
                   f"{wrap_tags('Мисол учун: сумка, ҳужжат, юк')}"

        update.message.reply_html(text)
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

        if user_data[ANNOUNCE] == PASSENGER:
            layout = get_passenger_layout(user[LANG], data=user_data)

            try:
                context.bot.delete_message(user[TG_ID], user_data[MESSAGE_ID])
            except TelegramError:
                context.bot.edit_message_reply_markup(user[TG_ID], user_data[MESSAGE_ID])

        elif user_data[ANNOUNCE] == PARCEL:
            layout = get_parcel_layout(user[LANG], data=user_data)

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
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data

    if data == 'cancel':

        icon = '🔴'
        if user[LANG] == LANGS[0]:
            text = "E'lon bekor qilindi"
            status = "Bekor qilindi"

        if user[LANG] == LANGS[1]:
            text = "Объявление отменено"
            status = "Отменено"

        if user[LANG] == LANGS[2]:
            text = "Эълон бекор қилинди"
            status = "Бекор қилинди"

        text = f'‼ {text}!'

    elif data == 'confirm':

        icon = '🟢'
        if user[LANG] == LANGS[0]:
            text = "E'lon tasdiqlandi"
            status = "Taqsdiqlangan"

        if user[LANG] == LANGS[1]:
            text = "Объявление одобрено"
            status = "Одобрено"

        if user[LANG] == LANGS[2]:
            text = "Эълон тасдиқланди"
            status = "Тасдиқланган"

        text = f'✅ {text}'

        data = dict()
        data[USER_ID] = user[ID]
        data[STATUS] = 'new'
        data[FROM_REGION] = user_data[FROM_REGION]
        data[FROM_DISTRICT] = user_data[FROM_DISTRICT]
        data[TO_REGION] = user_data[TO_REGION]
        data[TO_DISTRICT] = user_data[TO_DISTRICT]
        data[COMMENT] = user_data[COMMENT]

        if user_data[ANNOUNCE] == PASSENGER:
            data[QUANTITY] = user_data[PASSENGERS]
            data[DEPARTURE_TIME] = datetime.datetime.now() if user_data[TIME] == 'now' else \
                datetime.datetime.strptime(f'{user_data[DATE]} {user_data[TIME]}', '%d-%m-%Y %H:%M')
            table = 'passenger_announces'
        elif user_data[ANNOUNCE] == PARCEL:
            data[RECEIVER_CONTACT] = user_data[RECEIVER_CONTACT]
            table = 'parcel_announces'

        # insert new announcement
        insert_data(data, table)

    message_text = callback_query.message.text_html
    message_text += f'\n\n{icon} Status: {status}'
    callback_query.edit_message_text(message_text, parse_mode=ParseMode.HTML)

    reply_keyboard = ReplyKeyboard(passenger_parcel_keyboard, user[LANG]).get_keyboard()
    callback_query.message.reply_text(text, reply_markup=reply_keyboard)

    user_data.clear()
    return ConversationHandler.END


def announce_fallback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    text = update.message.text

    if text == '/start' or text == '/menu' or text == '/cancel':

        if user[LANG] == LANGS[0]:
            text = "E'lon berish bekor qilindi"
        if user[LANG] == LANGS[1]:
            text = "Объявление отменено"
        if user[LANG] == LANGS[2]:
            text = "Эълон бериш бекор қилинди"

        text = f'‼ {text} !'
        keyboard = passenger_parcel_keyboard if text == '/cancel' else main_menu_keyboard
        reply_keyboard = ReplyKeyboard(keyboard, user[LANG]).get_keyboard()
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
            text = "Hozir siz e'lon berish bo'limidasiz.\n\n" \
                   "E'lon berishni to'xtatish uchun /cancel ni bosing.\n\n" \
                   "Bosh menyuga qaytish uchun /menu ni bosing"

        if user[LANG] == LANGS[1]:
            text = "Вы сейчас в разделе объявлений.\n\n" \
                   "Нажмите /cancel, чтобы остановить объявлению.\n\n" \
                   "Нажмите /menu, чтобы вернуться в главное меню."

        if user[LANG] == LANGS[2]:
            text = "Ҳозир сиз эълон бериш бўлимидасиз.\n\n" \
                   "Эълон беришни тўхтатиш учун /cancel ни босинг.\n\n" \
                   "Бош менюга қайтиш учун /menu ни босинг."

        update.message.reply_text(text)
        return


announce_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(
        Filters.regex(r"(Yo'lovchi e'lon berish|Пассажир объявление|Йўловчи эълон бериш)$") |
        Filters.regex(r"(Pochta e'lon berish|Почта объявление|Почта эълон бериш)$") &
        (~Filters.update.edited_message), announce_conversation_callback)],

    states={
        REGION: [CallbackQueryHandler(region_callback, pattern=r'^(\d+)$')],

        DISTRICT: [CallbackQueryHandler(district_callback, pattern=r'^(\d+|back)$')],

        PASSENGERS: [CallbackQueryHandler(passenger_quantity_callback, pattern=r'^(\d+)$')],

        DATE: [CallbackQueryHandler(date_callback, pattern=r'^(now|\d+[-]\d+[-]\d+)$')],

        TIME: [CallbackQueryHandler(time_callback, pattern=r'^(back|next|\d+[:]00)$')],

        RECEIVER_CONTACT: [MessageHandler(
            Filters.contact | Filters.text & (~Filters.command) & (~Filters.update.edited_message), receiver_callback)],

        COMMENT: [
            CallbackQueryHandler(comment_callback, pattern=r'^no_comment$'),
            MessageHandler(Filters.text & (~Filters.command) & (~Filters.update.edited_message), comment_callback)
        ],

        CONFIRMATION: [CallbackQueryHandler(confirmation_callback, pattern='^(confirm|cancel)$')]
    },
    fallbacks=[MessageHandler(Filters.text & (~Filters.update.edited_message), announce_fallback)],

    persistent=True,

    name='announce_conversation'
)
