import logging

from telegram import Update, ParseMode, InlineKeyboardButton, TelegramError
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    Filters
)
from DB import *
from filters import *
from layouts import *
from globalvariables import *
from config import ACTIVE_ADMINS
from helpers import wrap_tags
from languages import LANGS

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *
from replykeyboards.replykeyboardtypes import reply_keyboard_types

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *

logger = logging.getLogger()


def do_command(update: Update, context: CallbackContext):
    # with open('update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    command = update.message.text

    if command == '/start':

        if user:
            text = reply_keyboard_types[active_driver_keyboard][4][f'text_{user[LANG]}']
            icon = reply_keyboard_types[active_driver_keyboard][4]['icon']

            text = f'{icon} {text}'
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
            heading = "Foydalanish shartlari"
            text = "Cardel Taxi ma'muriyati haydovchilar va yo'lovchilar orasidagi nizoli holatlarda va pochta " \
                   "jo’natmalari borasida yuzaga keladigan nizoli holatlarda  javobgarlikni o'z zimmasiga olmaydi"
            button_text = "Roziman"

        if data == LANGS[1]:
            heading = "Условия использования"
            text = "Администрация Cardel Taxi не несет ответственности в случае возникновения споров между " \
                   "водителями и пассажирами, а также в случае возникновения споров по почтовым отправлениям"
            button_text = "Я согласен"

        if data == LANGS[2]:
            heading = "Фойдаланиш шартлари"
            text = "Cardel Taxi маъмурияти ҳайдовчилар ва йўловчилар орасидаги низоли ҳолатларда ва " \
                   "почта жўнатмалари борасида юзага келадиган низоли ҳолатларда жавобгарликни ўз зиммасига олмайди"
            button_text = "Розиман"

        text = f'‼ {wrap_tags(heading)}:\n\n{text} !'
        inline_keyboard = callback_query.message.reply_markup.from_button(InlineKeyboardButton(
            text=button_text, callback_data='agree'
        ))

        try:
            callback_query.delete_message()
        except TelegramError:
            callback_query.edit_message_reply_markup()

        callback_query.message.reply_html(text, reply_markup=inline_keyboard)
        user_data[STATE] = AGREEMENT

        return AGREEMENT


def agreement_callback(update: Update, context: CallbackContext):
    user_data = context.user_data
    callback_query = update.callback_query

    if callback_query:

        if user_data[LANG] == LANGS[0]:
            text = "Assalomu alaykum!\n" \
                   "Ismingizni kiriting"
            example = "Misol: Sherzodbek Esanov yoki Sherzodbek"

        if user_data[LANG] == LANGS[1]:
            text = "Ассаламу алейкум!\n" \
                   "Введите ваше имя"
            example = 'Пример: Шерзодбек Эсанов или Шерзодбек'

        if user_data[LANG] == LANGS[2]:
            text = "Ассалому алайкум!\n" \
                   "Исмингизни киритинг"
            example = "Мисол: Шерзодбек Эсанов ёки Шерзодбек"

        text = f'🖐 {text}:\n\n{wrap_tags(example)}'
        callback_query.edit_message_text(text, parse_mode=ParseMode.HTML)

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
        if STATE in user_data:
            user_data.pop(STATE)

        if user_data[LANG] == LANGS[0]:
            text = f"{user_data[FULLNAME]}!\n" \
                   "Registratsiya muvafaqqiyatli yakunlandi"

        if user_data[LANG] == LANGS[1]:
            text = f"{user_data[FULLNAME]}!\n" \
                   "Регистрация прошла успешно"

        if user_data[LANG] == LANGS[2]:
            text = f"{user_data[FULLNAME]}!\n" \
                   "Регистрация мувафаққиятли якунланди"

        text = f'{text}! 👍'

        # Sending video files to the user
        for video in get_video_files():
            update.message.reply_video(video['file_id'], caption=video[f'caption_{user_data[LANG]}'])

        insert_data(user_data, 'users')

        reply_keyboard = ReplyKeyboard(main_menu_keyboard, user_data[LANG]).get_keyboard()
        update.message.reply_text(text, reply_markup=reply_keyboard)

        user_data.clear()

        return ConversationHandler.END


registration_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler(['start'], do_command, filters=~Filters.update.edited_message), ],

    states={
        LANG: [
            CallbackQueryHandler(lang_callback, pattern='^(uz|ru|cy)$'),
            MessageHandler(Filters.text & (~ Filters.command) & (~Filters.update.edited_message), lang_callback)
        ],

        AGREEMENT: [
            CallbackQueryHandler(agreement_callback, pattern='^agree$'),
            MessageHandler(Filters.text & (~ Filters.command) & (~Filters.update.edited_message), agreement_callback)
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
