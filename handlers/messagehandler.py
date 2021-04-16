from telegram import Update
from telegram.ext import Filters, MessageHandler, CallbackContext

from DB import get_user
from helpers import wrap_tags
from globalvariables import *
from languages import LANGS

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *

import re


def message_handler_callback(update: Update, context: CallbackContext):
    # with open('jsons/update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    # exit()
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    text = update.message.text

    passenger_parcel_obj = re.search("(Yo'lovchi va pochta|Пассажир и почта|Йўловчи ва почта)$", text)
    back_obj = re.search("(Ortga|Назад|Ортга)$", text)
    lang_obj = re.search("(Tilni o'zgartirish|Изменить язык|Тилни ўзгартириш)$", text)
    settings_obj = re.search("(Sozlamalar|Настройки|Созламалар)$", text)
    contact_us_obj = re.search("(Biz bilan bog'lanish|Свяжитесь с нами|Биз билан боғланиш)$", text)
    main_menu_obj = re.search("(Bosh menyu|Главное меню|Бош меню)$", text)

    if user:

        # if passenger_parcel_obj:
        #     reply_keyboard = ReplyKeyboard(passenger_parcel_keyboard, user[LANG]).get_keyboard()
        #     update.message.reply_text(text, reply_markup=reply_keyboard)

        # Settings button
        if settings_obj:
            keyboard = ReplyKeyboard(settings_keyboard, user[LANG]).get_keyboard()
            update.message.reply_text(text, reply_markup=keyboard)
            return

        # Change lang button
        elif lang_obj:
            if user[LANG] == LANGS[0]:
                text = "Tilni tanlang"

            if user[LANG] == LANGS[1]:
                text = "Выберите язык"

            if user[LANG] == LANGS[2]:
                text = "Тилни танланг"

            keyboard = InlineKeyboard(langs_keyboard).get_keyboard()
            update.message.reply_text(text, reply_markup=keyboard)
            return

        # Back button
        elif back_obj:
            reply_keyboard = ReplyKeyboard(main_menu_keyboard, user[LANG]).get_keyboard()
            update.message.reply_text(text, reply_markup=reply_keyboard)
            return

        # contact us
        elif contact_us_obj:
            admin = wrap_tags('@cardel_admin')

            if user[LANG] == LANGS[0]:
                text = f"Savollar, takliflar va shikoyatlaringiz boʼlsa {admin} ga murojaat qilishingiz mumkin."
            if user[LANG] == LANGS[1]:
                text = f"Если у вас есть какие-либо вопросы, предложения или жалобы, свяжитесь с {admin}."
            if user[LANG] == LANGS[2]:
                text = f"Саволлар, таклифлар ва шикоятларингиз бўлса {admin} га мурожаат қилишингиз мумкин."

            update.message.reply_html(text)

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


message_handler = MessageHandler(Filters.text & (~ Filters.command) & (~Filters.update.edited_message)
                                 & (~Filters.reply), message_handler_callback)
