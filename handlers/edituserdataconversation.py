import logging
import re

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import MessageHandler, ConversationHandler, CallbackContext, Filters

from DB import *
from filters import *
from layouts import *
from globalvariables import *
from helpers import delete_message_by_message_id
from languages import LANGS

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *

logger = logging.getLogger()

edit_fullname_pattern = "(Ism, Familyani o'zgartirish|Изменить имя, фамилию|Исм, Фамиляни ўзгартириш)"
edit_phone_number_pattern = "(Asosiy raqamni o'zgartirish|Измените основной номер|Асосий рақамни ўзгартириш)"
edit_phone_number_2_pattern = "(Qo'shimcha raqamni o'zgartirish|Измените дополнительный номер|Қўшимча рақамни ўзгартириш)"


def edit_user_data_conversation_callback(update: Update, context: CallbackContext):
    # with open('update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    only_user_data_layout = get_only_user_data_layout(user)
    reply_keyboard = ReplyKeyboard(edit_user_data_keyboard, user[LANG]).get_keyboard()
    update.message.reply_html(only_user_data_layout, reply_markup=reply_keyboard)

    user_data[STATE] = CHOOSE_EDITING_FULLNAME_OR_PHONE_NUMBERS

    # logger.info('user_data: %s', user_data)
    return CHOOSE_EDITING_FULLNAME_OR_PHONE_NUMBERS


def choose_editing_fullname_or_phone_numbers_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    edit_fullname_obj = re.search(edit_fullname_pattern, update.message.text)
    edit_phone_number_obj = re.search(edit_phone_number_pattern, update.message.text)
    edit_phone_number_2_obj = re.search(edit_phone_number_2_pattern, update.message.text)

    if edit_fullname_obj:

        if user[LANG] == LANGS[0]:
            new_fullname_text = "Yangi ism, familyangizni kiriting"

        if user[LANG] == LANGS[1]:
            new_fullname_text = "Введите новое имя, фамилию"

        if user[LANG] == LANGS[2]:
            new_fullname_text = "Янги исм, фамилянгизни киритинг"

        reply_text = f'{new_fullname_text} :'
        state = return_state = EDIT_FULLNAME

    elif edit_phone_number_obj or edit_phone_number_2_obj:

        reply_text = get_phone_number_layout(user[LANG])
        state = EDIT_PHONE_NUMBER_2 if edit_phone_number_2_obj else EDIT_PHONE_NUMBERS
        return_state = EDIT_PHONE_NUMBERS

    update.message.reply_html(reply_text, reply_markup=ReplyKeyboardRemove())
    user_data[STATE] = state

    # logger.info('user_data: %s', user_data)
    return return_state


def edit_fullname_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    fullname = fullname_filter(update.message.text)

    if fullname:

        if user[LANG] == LANGS[0]:
            edited_text = "Ism, familya o'zgartirildi"
            not_edited_text = "Ism, familya o'zgartirilmadi"

        if user[LANG] == LANGS[1]:
            edited_text = "Имя, фамилия изменена"
            not_edited_text = "Имя, фамилия не изменилась"

        if user[LANG] == LANGS[2]:
            edited_text = "Исм, фамиля ўзгартирилди"
            not_edited_text = "Исм, фамиля ўзгартирилмади"

        result = update_user_fullname(fullname, user[ID])

        if result == 'updated':
            reply_text = f'✅ {edited_text} !'
            user[FULLNAME] = fullname
        else:
            reply_text = f'❌ {not_edited_text} !'
        update.message.reply_text(reply_text)

        only_user_data_layout = get_only_user_data_layout(user)
        reply_keyboard = ReplyKeyboard(edit_user_data_keyboard, user[LANG]).get_keyboard()
        update.message.reply_html(only_user_data_layout, reply_markup=reply_keyboard)

        user_data[STATE] = CHOOSE_EDITING_FULLNAME_OR_PHONE_NUMBERS

        return CHOOSE_EDITING_FULLNAME_OR_PHONE_NUMBERS

    else:

        fullname_error_text = get_fullname_error_text(user[LANG])
        update.message.reply_html(fullname_error_text, quote=True)

        return


def edit_phone_number_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    phone_number = phone_number_filter(update.message.text)

    if not phone_number:

        error_text = get_phone_number_error_text(user[LANG])
        layout = get_phone_number_layout(user[LANG])
        error_text = f'❌ {error_text}!\n\n' + layout
        update.message.reply_html(error_text, quote=True)

        return

    else:
        if user[LANG] == LANGS[0]:
            registed_text = "Kechirasiz, bu raqam allaqachon ro'yxatdan o'tgan !\n\n" \
                            "Boshqa raqamni kiriting"
            edited_text = "Telefon raqami o'zartirildi"
            not_edited_text = "Telefon raqami o'zartirilmadi"
        if user[LANG] == LANGS[1]:
            registed_text = "Извините, этот номер уже зарегистрирован !\n\n" \
                            "Введите другой номер"
            edited_text = "Номер телефона изменен"
            not_edited_text = "Номер телефона не был изменен"
        if user[LANG] == LANGS[2]:
            registed_text = "Кечирасиз, бу рақам аллақачон рўйхатдан ўтган !\n\n" \
                            "Бошқа рақамни киритинг"
            edited_text = "Телефон рақами ўзартирилди"
            not_edited_text = "Телефон рақами ўзартирилмади"

        registed_text = f'‼ {registed_text}.'
        edited_text = f'✅ {edited_text} !'
        not_edited_text = f'❌ {not_edited_text} !'

        check_result = check_phone_number_existence(phone_number)

        if check_result is None:
            if user_data[STATE] == EDIT_PHONE_NUMBER_2:
                field = PHONE_NUMBER_2
            elif user_data[STATE] == EDIT_PHONE_NUMBERS:
                field = PHONE_NUMBER

            update_result = update_user_phone_numbers(field, phone_number, user[ID])

            if update_result == 'updated':
                reply_text = edited_text
                user[field] = phone_number
            else:
                reply_text = not_edited_text

            update.message.reply_text(reply_text)

            only_user_data_layout = get_only_user_data_layout(user)
            reply_keyboard = ReplyKeyboard(edit_user_data_keyboard, user[LANG]).get_keyboard()
            update.message.reply_html(only_user_data_layout, reply_markup=reply_keyboard)

            user_data[STATE] = CHOOSE_EDITING_FULLNAME_OR_PHONE_NUMBERS

            return CHOOSE_EDITING_FULLNAME_OR_PHONE_NUMBERS

        else:
            update.message.reply_text(registed_text)

            return


def edit_user_data_conversation_fallback(update: Update, context: CallbackContext):
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
        keyboard = main_menu_keyboard if text == '/start' or text == '/menu' else edit_user_data_keyboard

        reply_keyboard = ReplyKeyboard(keyboard, user[LANG]).get_keyboard()
        update.message.reply_text(cenceled_text, reply_markup=reply_keyboard)

        delete_message_by_message_id(context, user)

        if text == '/cancel':
            user_data[STATE] = CHOOSE_EDITING_FULLNAME_OR_PHONE_NUMBERS

            return CHOOSE_EDITING_FULLNAME_OR_PHONE_NUMBERS

        user_data.clear()

        return ConversationHandler.END

    elif re.search("(Ortga|Назад|Ортга)$", update.message.text):

        reply_keyboard = ReplyKeyboard(my_data_keyboard, user[LANG]).get_keyboard()
        update.message.reply_text(text, reply_markup=reply_keyboard)

        delete_message_by_message_id(context, user)

        user_data.clear()
        user_data[STATE] = 'my_data'

        return ConversationHandler.END


edit_user_data_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(
        r"(Shaxsiy ma'lumotlarni o'zgartirish|Измененить личных данных|Шахсий маълумотларни ўзгартириш)$") &
                                 (~Filters.update.edited_message), edit_user_data_conversation_callback)],

    states={
        CHOOSE_EDITING_FULLNAME_OR_PHONE_NUMBERS: [
            MessageHandler(
                Filters.regex(f"({edit_fullname_pattern}|{edit_phone_number_pattern}|{edit_phone_number_2_pattern})$") &
                (~Filters.update.edited_message), choose_editing_fullname_or_phone_numbers_callback)],

        EDIT_FULLNAME: [
            MessageHandler(Filters.text & (~ Filters.command) & (~Filters.update.edited_message),
                           edit_fullname_callback)],

        EDIT_PHONE_NUMBERS: [
            MessageHandler(Filters.text & (~ Filters.command) & (~Filters.update.edited_message),
                           edit_phone_number_callback)
        ],
    },
    fallbacks=[MessageHandler(Filters.text & (~Filters.update.edited_message), edit_user_data_conversation_fallback)],

    persistent=True,

    name='edit_user_data_conversation'
)
