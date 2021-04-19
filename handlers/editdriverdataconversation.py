import logging
import re

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import CallbackQueryHandler, MessageHandler, ConversationHandler, CallbackContext, Filters

from DB import *
from languages import LANGS
from helpers import *
from globalvariables import *
from layouts import get_only_driver_layout

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *

logger = logging.getLogger()

edit_car_model_pattern = "(Mashina markasini o'zgartirish|Изменить марку автомобиля|Машина маркасини ўзгартириш)"
edit_baggage_pattern = "(Bagajni o'zgartirish|Изменение багажа|Багажни ўзгартириш)"


def edit_driver_data_conversation_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    driver_and_car_data = get_driver_and_car_data(user[ID])

    if driver_and_car_data is None:

        if user[LANG] == LANGS[0]:
            not_registred_text = "Siz haydovchi sifatida ro'yxatdan o'tmagansiz"
        if user[LANG] == LANGS[1]:
            not_registred_text = "Вы не зарегистрированы как водитель"
        if user[LANG] == LANGS[2]:
            not_registred_text = "Сиз ҳайдовчи сифатида рўйхатдан ўтмагансиз"

        not_registred_text = f'‼ {not_registred_text} !'
        update.message.reply_text(not_registred_text)

        return ConversationHandler.END

    else:

        only_driver_layout = get_only_driver_layout(driver_and_car_data, user[LANG])
        reply_keyboard = ReplyKeyboard(edit_driver_data_keyboard, user[LANG]).get_keyboard()
        update.message.reply_html(only_driver_layout, reply_markup=reply_keyboard)

        user_data[STATE] = CHOOSE_EDITING_CAR_MODEL_OR_BAGGAGE

        # logger.info('user_data: %s', user_data)
        return CHOOSE_EDITING_CAR_MODEL_OR_BAGGAGE


def choose_editing_car_model_or_baggage_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    edit_car_model_obj = re.search(edit_car_model_pattern, update.message.text)
    edit_baggage_obj = re.search(edit_baggage_pattern, update.message.text)

    if edit_car_model_obj:

        if user[LANG] == LANGS[0]:
            choose_car_model_text = "Avtomabilingiz rusumini tanlang"
        if user[LANG] == LANGS[1]:
            choose_car_model_text = "Выберите модель вашего автомобиля"
        if user[LANG] == LANGS[2]:
            choose_car_model_text = "Автомабилингиз русумини танланг"

        text = f'🚕 {choose_car_model_text} :'
        inline_keyboard = InlineKeyboard(car_models_keyboard, user[LANG]).get_keyboard()

        state = EDIT_CAR_MODEL

    elif edit_baggage_obj:

        if user[LANG] == LANGS[0]:
            ask_baggage_text = "Bagaj(yuqori bagaj) bormi"
        if user[LANG] == LANGS[1]:
            ask_baggage_text = "Есть ли багаж (верхний багаж)"
        if user[LANG] == LANGS[2]:
            ask_baggage_text = "Багаж(юқори багаж) борми"

        text = f'{ask_baggage_text} ?'
        inline_keyboard = InlineKeyboard(yes_no_keyboard, user[LANG]).get_keyboard()

        state = EDIT_BAGGAGE

    update.message.reply_text(update.message.text, reply_markup=ReplyKeyboardRemove())
    message = update.message.reply_text(text, reply_markup=inline_keyboard)

    user_data[STATE] = state
    user_data[MESSAGE_ID] = message.message_id

    # logger.info('user_data: %s', user_data)
    return state


def edit_car_model_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query

    if user[LANG] == LANGS[0]:
        edited_text = "Mashina markasi o'zgartirildi"
        not_edited_text = "Mashina markasi o'zgartirilmadi"
    if user[LANG] == LANGS[1]:
        edited_text = "Марка автомобиля была изменена"
        not_edited_text = "Марка автомобиля неизменен"
    if user[LANG] == LANGS[2]:
        edited_text = "Машина маркаси ўзгартирилди"
        not_edited_text = "Машина маркаси ўзгартирилмади"

    result = update_driver_car_model(callback_query.data, user[ID])

    driver_and_car_data = get_driver_and_car_data(user[ID])
    only_driver_layout = get_only_driver_layout(driver_and_car_data, user[LANG])

    edit_text = f'✅ {edited_text} !' if result == 'updated' else f'❌ {not_edited_text} !'
    callback_query.edit_message_text(edit_text)

    reply_keyboard = ReplyKeyboard(edit_driver_data_keyboard, user[LANG]).get_keyboard()
    callback_query.message.reply_html(only_driver_layout, reply_markup=reply_keyboard)

    user_data[STATE] = CHOOSE_EDITING_CAR_MODEL_OR_BAGGAGE
    if MESSAGE_ID in user_data:
        user_data.pop(MESSAGE_ID)

    return CHOOSE_EDITING_CAR_MODEL_OR_BAGGAGE


def edit_baggage_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query

    if user[LANG] == LANGS[0]:
        edited_text = "Bagaj(yuqori bagaj) o'zgartirildi"
        not_edited_text = "Bagaj(yuqori bagaj) o'zgartirilmadi"
    if user[LANG] == LANGS[1]:
        edited_text = "Багаж (верхний багаж) изменен"
        not_edited_text = "Багаж (верхний багаж) неизменен"
    if user[LANG] == LANGS[2]:
        edited_text = "Багаж(юқори багаж) ўзгартирилди"
        not_edited_text = "Багаж(юқори багаж) ўзгартирилмади"

    baggage = True if callback_query.data == 'yes' else False
    result = update_baggage(baggage, user[ID])

    driver_and_car_data = get_driver_and_car_data(user[ID])
    only_driver_layout = get_only_driver_layout(driver_and_car_data, user[LANG])

    edit_text = f'✅ {edited_text} !' if result == 'updated' else f'❌ {not_edited_text} !'
    callback_query.edit_message_text(edit_text)

    reply_keyboard = ReplyKeyboard(edit_driver_data_keyboard, user[LANG]).get_keyboard()
    callback_query.message.reply_html(only_driver_layout, reply_markup=reply_keyboard)

    user_data[STATE] = CHOOSE_EDITING_CAR_MODEL_OR_BAGGAGE
    if MESSAGE_ID in user_data:
        user_data.pop(MESSAGE_ID)

    return CHOOSE_EDITING_CAR_MODEL_OR_BAGGAGE


def edit_driver_data_conversation_fallback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    text = update.message.text

    if text == '/start' or text == '/menu' or text == '/cancel':

        if user[LANG] == LANGS[0]:
            cenceled_text = "O'zgartirish bekor qilindi"
        if user[LANG] == LANGS[1]:
            cenceled_text = "Изменение было отменено"
        if user[LANG] == LANGS[2]:
            cenceled_text = "Ўзгартириш бекор қилинди"

        cenceled_text = f'‼ {cenceled_text} !'
        keyboard = main_menu_keyboard if text == '/start' or text == '/menu' else edit_driver_data_keyboard

        reply_keyboard = ReplyKeyboard(keyboard, user[LANG]).get_keyboard()
        update.message.reply_text(cenceled_text, reply_markup=reply_keyboard)

        delete_message_by_message_id(context, user)

        if text == '/cancel':
            user_data[STATE] = CHOOSE_EDITING_CAR_MODEL_OR_BAGGAGE

            return CHOOSE_EDITING_CAR_MODEL_OR_BAGGAGE

        user_data.clear()

        return ConversationHandler.END

    elif re.search("(Ortga|Назад|Ортга)$", update.message.text):

        reply_keyboard = ReplyKeyboard(my_data_keyboard, user[LANG]).get_keyboard()
        update.message.reply_text(text, reply_markup=reply_keyboard)

        delete_message_by_message_id(context, user)

        user_data.clear()
        user_data[STATE] = 'my_data'

        return ConversationHandler.END


edit_driver_data_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(
        "(Haydovchi ma'lumotlarini o'zgartirish|Изменить информацию о драйвере|Ҳайдовчи маълумотларини ўзгартириш)$") &
                                 (~Filters.update.edited_message), edit_driver_data_conversation_callback), ],

    states={
        CHOOSE_EDITING_CAR_MODEL_OR_BAGGAGE: [
            MessageHandler(Filters.regex(f"({edit_car_model_pattern}|{edit_baggage_pattern})$") &
                           (~Filters.update.edited_message), choose_editing_car_model_or_baggage_callback)],

        EDIT_CAR_MODEL: [CallbackQueryHandler(edit_car_model_callback, pattern=r'^\d+$')],

        EDIT_BAGGAGE: [CallbackQueryHandler(edit_baggage_callback, pattern=r'^(yes|no)$')],

    },
    fallbacks=[
        MessageHandler(Filters.text & (~Filters.update.edited_message), edit_driver_data_conversation_fallback)
    ],

    persistent=True,

    name='edit_driver_data_conversation'
)
