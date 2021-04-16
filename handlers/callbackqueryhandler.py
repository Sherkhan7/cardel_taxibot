from telegram import Update, TelegramError
from telegram.ext import CallbackQueryHandler, CallbackContext

from DB import *
from globalvariables import *

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

        if data == 'uz':
            reply_text = "Til o'zgartirildi"
        if data == 'ru':
            reply_text = "Язык был изменен"
        if data == 'cy':
            reply_text = "Тил ўзгартирилди"

        reply_text = f'{reply_text} {flag}'

        try:
            callback_query.delete_message()
        except TelegramError:
            callback_query.edit_message_reply_markup()

        callback_query.message.reply_text(reply_text)

        return

    # logger.info('user_data: %s', user_data)


callback_query_handler = CallbackQueryHandler(inline_keyboards_handler_callback)
