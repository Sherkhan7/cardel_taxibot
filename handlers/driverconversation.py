import logging

from telegram import Update, ReplyKeyboardRemove, TelegramError
from telegram.ext import (
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    Filters,
)
from DB import *
from languages import LANGS
from helpers import *
from globalvariables import *

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *
from replykeyboards.replykeyboardtypes import reply_keyboard_types

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *

logger = logging.getLogger()


def driver_conversation_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    driver = get_driver_by_user_id(user[ID])

    if driver is None:

        if user[LANG] == LANGS[0]:
            text = "Haydochi sifatida ro'yxatdan o'tmoqchimisiz"
        if user[LANG] == LANGS[1]:
            text = "Вы хотите зарегистрироваться как водител"
        if user[LANG] == LANGS[2]:
            text = "Ҳайдочи сифатида рўйхатдан ўтмоқчимисиз"

        text = f'🟡 {text}?'

        update.message.reply_text(update.message.text, reply_markup=ReplyKeyboardRemove())
        inline_keyboard = InlineKeyboard(yes_no_keyboard, user[LANG]).get_keyboard()
        message = update.message.reply_text(text, reply_markup=inline_keyboard)

        user_data[STATE] = YES_NO
        user_data[MESSAGE_ID] = message.message_id

        return YES_NO

    elif get_active_driver_by_driver_id(driver_id=driver[ID]):
        keyboard = active_driver_keyboard
    else:
        keyboard = driver_keyboard

    reply_keyboard = ReplyKeyboard(keyboard, user[LANG]).get_keyboard()
    update.message.reply_text(update.message.text, reply_markup=reply_keyboard)

    return ConversationHandler.END


def yes_no_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data

    if data == 'no':

        try:
            callback_query.delete_message()
        except TelegramError:
            try:
                callback_query.edit_message_reply_markup()
            except TelegramError:
                pass

        icon = reply_keyboard_types[passenger_parcel_keyboard][5]['icon']
        text = reply_keyboard_types[passenger_parcel_keyboard][5][f'text_{user[LANG]}']
        text = f'{icon} {text}'
        reply_keyboard = ReplyKeyboard(main_menu_keyboard, user[LANG]).get_keyboard()
        callback_query.message.reply_text(text, reply_markup=reply_keyboard)

        user_data.clear()

        return ConversationHandler.END

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
        callback_query.answer()

        user_data[STATE] = CAR_MODEL

        return CAR_MODEL


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
    callback_query.answer()

    user_data[STATE] = BAGGAGE

    return BAGGAGE


def baggage_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query

    if user[LANG] == LANGS[0]:
        reg_complete_text = "Registratsiya muvofaqqiyatli yakunlandi"
        driver_text = "Haydovchi"

    if user[LANG] == LANGS[1]:
        reg_complete_text = "Регистрация успешно завершена"
        driver_text = "Водитель"

    if user[LANG] == LANGS[2]:
        reg_complete_text = "Регистрация мувофаққиятли якунланди"
        driver_text = "Ҳайдовчи"

    reg_complete_text = f'{reg_complete_text}! 👍'
    driver_text = f'🚕 {driver_text}'

    data = dict()
    data[BAGGAGE] = True if callback_query.data == 'yes' else False
    data[USER_ID] = user[ID]
    data[CAR_ID] = user_data[CAR_ID]
    data[STATUS] = 'standart'

    # Inset driver data to database
    insert_data(data, 'drivers')

    callback_query.edit_message_text(reg_complete_text)

    reply_keyboard = ReplyKeyboard(driver_keyboard, user[LANG]).get_keyboard()
    callback_query.message.reply_text(driver_text, reply_markup=reply_keyboard)

    user_data.clear()

    return ConversationHandler.END


def driver_fallback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    text = update.message.text

    if text == '/start' or text == '/menu' or text == '/cancel':

        if user[LANG] == LANGS[0]:
            text = "Haydovchi sifatida ro'yxatdan o'tish bekor qilindi"
        if user[LANG] == LANGS[1]:
            text = "Регистрация в качестве водителя отменена"
        if user[LANG] == LANGS[2]:
            text = "Ҳайдовчи сифатида рўйхатдан ўтиш бекор қилинди"

        text = f'‼ {text} !'
        delete_message_by_message_id(context, user)

        reply_keyboard = ReplyKeyboard(main_menu_keyboard, user[LANG]).get_keyboard()
        update.message.reply_text(text, reply_markup=reply_keyboard)

        user_data.clear()

        return ConversationHandler.END

    else:

        if user[LANG] == LANGS[0]:
            text = "Hozir siz haydovchi sifatida ro'yxatdan o'tyapsiz.\n\n" \
                   "Ro'yxatdan o'tishni to'xtatish uchun /cancel ni bosing"

        if user[LANG] == LANGS[1]:
            text = "Вы сейчас регистрируетесь как водитель такси.\n\n" \
                   "Нажмите /cancel, чтобы остановить регистрацию"

        if user[LANG] == LANGS[2]:
            text = "Ҳозир сиз ҳайдовчи сифатида рўйхатдан ўтяпсиз\n\n" \
                   "Рўйхатдан ўтишни тўхтатиш учун /cancel ни босинг"

        text = f'‼ {text}.'
        update.message.reply_text(text, quote=True)

        return


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
