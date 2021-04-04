from telegram import Update, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Filters, MessageHandler, CallbackContext

from DB import get_user
from helpers import wrap_tags
from globalvariables import *
from languages import LANGS

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *

import re


def message_handler_callback(update: Update, context: CallbackContext):
    # with open('jsons/update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    text = update.message.text

    passenger_parcel_obj = re.search(r"(Yo'lovchi va pochta|Пассажир и почта|Йўловчи ва почта)$", text)
    settings_obj = re.search(r"(Sozlamalar|Настройки|Созламалар)$", text)
    contact_us_obj = re.search(r"(Biz bilan bog'lanish|Свяжитесь с нами|Биз билан боғланиш)$", text)
    main_menu_obj = re.search(r"(Bosh menyu|Главное меню|Бош меню)$", text)

    if user:

        if passenger_parcel_obj:
            reply_keyboard = ReplyKeyboard(passenger_parcel_keyboard, user[LANG]).get_keyboard()
            update.message.reply_text(text, reply_markup=reply_keyboard)

        # elif settings_obj:
        #     pass
        #
        # # Biz bilan bo'glanish
        # elif contact_us_obj:
        #
        #     text = f"Kitapp premium adminlari bilan boglanish uchun:\n" \
        #            f"{wrap_tags('@kitapp_admin', '[ +998999131099 ]')} yoki\n\n" \
        #            f"{wrap_tags('@alisherqultayev', '[ +998903261609 ]')} larga murojaat qilishingiz mumkin."
        #
        #     update.message.reply_html(text)
        elif main_menu_obj:
            reply_keyboard = ReplyKeyboard(main_menu_keyboard, user[LANG]).get_keyboard()
            update.message.reply_text(text, reply_markup=reply_keyboard)
        else:

            thinking_emoji = '🤔🤔🤔'
            if user[LANG] == LANGS[0]:
                text = "/start ni bosing"

            if user[LANG] == LANGS[1]:
                text = "Нажмите /start"

            if user[LANG] == LANGS[2]:
                text = "/start ни босинг"

            text = f'{thinking_emoji}\n\n' \
                   f'❗ {text}!'
            update.message.reply_text(text, quote=True)

    else:

        reply_text = "❗ Siz ro'yxatdan o'tmagansiz !\nBuning uchun /start ni bosing.\n\n" \
                     "❗ Вы не зарегистрированы !\nДля этого нажмите /start\n\n" \
                     "❗ Сиз рўйхатдан ўтмагансиз !\nБунинг учун /start ни босинг"

        update.message.reply_text(reply_text)


message_handler = MessageHandler(Filters.text & (~ Filters.command) & (~Filters.update.edited_message),
                                 message_handler_callback)
