import logging
import re

from telegram import Update, TelegramError
from telegram.ext import CallbackQueryHandler, CallbackContext

from DB import *
from globalvariables import *
from languages import LANGS

logger = logging.getLogger()


def inline_keyboards_handler_callback(update: Update, context: CallbackContext):
    # with open('jsons/callback_query.json', 'w') as callback_query_file:
    #     callback_query_file.write(callback_query.to_json())
    user = get_user(update.effective_user.id)
    callback_query = update.callback_query
    data = callback_query.data

    if data == 'uz' or data == 'ru' or data == 'cy':

        update_user_lang(data, user[ID])

        flag = '🇺🇿' if data == 'uz' or data == 'cy' else '🇷🇺'

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

        # logger.info('user_data: %s', user_data)
        return

    elif re.search(r"^dr_\d+$", data):

        if user[LANG] == LANGS[0]:
            alert_text = "Kechirasiz, faqat «Taksi qidirish» bo'limida bo'lganingizdagina lokatsiya yubora olasiz"
        if user[LANG] == LANGS[1]:
            alert_text = "Извините, вы можете указать местоположение, только когда находитесь в разделе «Поиск такси»"
        if user[LANG] == LANGS[2]:
            alert_text = "Кечирасиз, фақат «Такси қидириш» бўлимида бўлганингиздагина локация юбора оласиз"

        alert_text = f'🛑 {alert_text} !'

        try:
            callback_query.answer(alert_text, show_alert=True)
        except TelegramError:
            pass

        return


callback_query_handler = CallbackQueryHandler(inline_keyboards_handler_callback)
