from telegram.ext import CallbackQueryHandler, CallbackContext
from telegram import Update
from DB import *
from globalvariables import *

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *

from inlinekeyboards.inlinekeyboardvariables import *
from inlinekeyboards.inlinekeyboardtypes import inline_keyboard_types

import logging

logger = logging.getLogger()


def inline_keyboards_handler_callback(update: Update, context: CallbackContext):
    # with open('jsons/callback_query.json', 'w') as callback_query_file:
    #     callback_query_file.write(callback_query.to_json())
    user = get_user(update.effective_user.id)
    callback_query = update.callback_query
    data = callback_query.data

    if data == 'uz' or data == 'ru' or data == 'cy':

        update_user_info(user[ID], lang=data)
        flag_uzb = '🇺🇿'
        flag_rus = '🇷🇺'
        flag = flag_rus if data == 'ru' else flag_uzb
        x = 0
        if data == 'uz':
            text = f"Til"
            reply_text = "Til o'zgartirildi"
        if data == 'ru':
            text = "Язык"
            reply_text = "Язык был изменен"
            x = 1
        if data == 'cy':
            text = "Тил"
            reply_text = "Тил ўзгартирилди"

        text = f'{text}: {inline_keyboard_types[langs_keyboard][x]["text"]} {flag}'
        callback_query.edit_message_text(text)

        reply_keyboard = ReplyKeyboard(settings_keyboard, data).get_keyboard()
        callback_query.message.reply_text(reply_text, reply_markup=reply_keyboard)

        return

    # logger.info('user_data: %s', user_data)


callback_query_handler = CallbackQueryHandler(inline_keyboards_handler_callback)
