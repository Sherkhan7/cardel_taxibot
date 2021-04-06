from telegram import Update
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

from filters import *
from helpers import wrap_tags
from languages import LANGS
from layouts import *
from globalvariables import *

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *

import logging

logger = logging.getLogger()


def do_command(update: Update, context: CallbackContext):
    # with open('update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    command = update.message.text

    if command == '/start':

        if user:

            if user[LANG] == LANGS[0]:
                text = "Siz ro'yxatdan o'tgansiz"

            if user[LANG] == LANGS[1]:
                text = "Вы зарегистрированы"

            if user[LANG] == LANGS[2]:
                text = "Сиз рўйхатдан ўтгансиз"

            text = f'⚠  {text}, {user[FULLNAME]}!'
            keyboard = ReplyKeyboard(main_menu_keyboard, user[LANG]).get_keyboard()
            update.message.reply_text(text, reply_markup=keyboard)

            return ConversationHandler.END

        else:

            text = "Iltimos, davom etish uchun tilni tanlang\n\n" \
                   "Пожалуйста, выберите язык чтобы продолжить\n\n" \
                   "Илтимос, давом этиш учун тилни танланг"
            keyboard = InlineKeyboard(langs_keyboard).get_keyboard()
            update.message.reply_text(text, reply_markup=keyboard)

            user_data[STATE] = LANG
            user_data[TG_ID] = update.effective_user.id
            user_data[USERNAME] = update.effective_user.username
            user_data[IS_ADMIN] = True if update.effective_user.id in ACTIVE_ADMINS else False

            return LANG


def lang_callback(update: Update, context: CallbackContext):
    user_data = context.user_data
    callback_query = update.callback_query

    if callback_query:

        data = callback_query.data
        user_data[LANG] = data

        if data == LANGS[0]:
            edit_text = "Til: 🇺🇿"
            text = "Salom!\n" \
                   "Ism,familyangizni quyidagi formatda yuboring"
            example = "Misol: Sherzodbek Esanov yoki Sherzodbek"

        if data == LANGS[1]:
            edit_text = 'Язык: 🇷🇺'
            text = 'Привет!\n' \
                   'Отправьте свое имя,фамилию в формате ниже'
            example = 'Пример: Шерзодбек Эсанов или Шерзодбек'

        if data == LANGS[2]:
            edit_text = "Тил: 🇺🇿"
            text = "Салом!\n" \
                   "Исм,фамилянгизни қуйидаги форматда юборинг"
            example = "Мисол: Шерзодбек Эсанов ёки Шерзодбек"

        text = f'🖐  {text}:\n\n {wrap_tags(example)}'

        callback_query.edit_message_text(edit_text)
        callback_query.message.reply_html(text)

        user_data[STATE] = FULLNAME

        return FULLNAME


def fullname_callback(update: Update, context: CallbackContext):
    user_data = context.user_data
    fullname = fullname_filter(update.message.text)

    if fullname:

        user_data[FULLNAME] = fullname

        if user_data[LANG] == LANGS[0]:
            text = "📱 Telefon raqamini yuborish tugmasini bosing\nyoki"

        if user_data[LANG] == LANGS[1]:
            text = "Нажмите на кнопку 📱 Отправить номер телефона\nили"

        if user_data[LANG] == LANGS[2]:
            text = "📱 Телефон рақамини юбориш тугмасини босинг\nёки"

        layout = get_phone_number_layout(user_data[LANG])
        text += f' {layout}'
        reply_keyboard = ReplyKeyboard(phone_number_keyboard, user_data[LANG]).get_keyboard()
        update.message.reply_html(text, reply_markup=reply_keyboard)

        user_data[STATE] = PHONE_NUMBER

        return PHONE_NUMBER

    else:

        fullname_error_text = get_fullname_error_text(user_data[LANG])
        update.message.reply_html(fullname_error_text, quote=True)

        return


def phone_number_callback(update: Update, context: CallbackContext):
    user_data = context.user_data
    phone_number = update.message.contact.phone_number if update.message.contact else update.message.text
    phone_number = phone_number_filter(phone_number)

    if not phone_number:

        error_text = get_phone_number_error_text(user_data[LANG])
        layout = get_phone_number_layout(user_data[LANG])
        error_text = f'❌ {error_text}!\n\n' + layout
        update.message.reply_html(error_text, quote=True)

        return

    else:

        user_data[PHONE_NUMBER] = phone_number
        user_data.pop(STATE)
        insert_data(user_data, 'users')

        if user_data[LANG] == LANGS[0]:
            text = f"Xush kelibsiz, {user_data[FULLNAME]}!\n" \
                   "Biz sizni ko'rganimizdan xursandmiz"

        if user_data[LANG] == LANGS[1]:
            text = f"Добро пожаловать, {user_data[FULLNAME]}!\n" \
                   "Мы рады видеть вас"

        if user_data[LANG] == LANGS[2]:
            text = f"Хуш келибсиз, {user_data[FULLNAME]}!\n" \
                   "Биз сизни кўрганимиздан хурсандмиз"

        text = f'🤝  {text}!'
        reply_keyboard = ReplyKeyboard(main_menu_keyboard, user_data[LANG]).get_keyboard()
        update.message.reply_text(text, reply_markup=reply_keyboard)

        user_data.clear()

        return ConversationHandler.END


registration_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler(['start'], do_command, filters=~Filters.update.edited_message), ],

    states={
        LANG: [
            CallbackQueryHandler(lang_callback, pattern='^(uz|ru|cy)$'),
            # used for handle messages in this state
            MessageHandler(Filters.text & (~ Filters.command) & (~Filters.update.edited_message), lang_callback)
        ],

        FULLNAME: [MessageHandler(Filters.text & (~Filters.update.edited_message), fullname_callback)],

        PHONE_NUMBER: [
            MessageHandler(Filters.contact | Filters.text & (~Filters.update.edited_message), phone_number_callback)
        ],
    },
    fallbacks=[],

    persistent=True,

    name='registration_conversation'
)
