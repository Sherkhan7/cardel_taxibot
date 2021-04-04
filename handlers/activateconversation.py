from telegram import (
    Update,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    ParseMode,
    TelegramError,
)
from telegram.ext import (
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    Filters,
)
from DB import insert_data, get_user
from languages import LANGS
from layouts import get_passenger_layout, get_phone_number_layout, get_parcel_layout
from globalvariables import *
from helpers import wrap_tags
from filters import phone_number_filter

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *

import logging
import datetime
import re

logger = logging.getLogger()


def activate_conversation_callback(update: Update, context: CallbackContext):
    # with open('jsons/update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    text = update.message.text

    if user[LANG] == LANGS[0]:
        text = "Qayerdan (Viloyatni tanlang)"

    if user[LANG] == LANGS[1]:
        text = "Откуда (Выберите область)"

    if user[LANG] == LANGS[2]:
        text = "Қаердан (Вилоятни танланг)"

    update.message.reply_text(update.message.text, reply_markup=ReplyKeyboardRemove())

    text = f'{text}:'
    inline_keyboard = InlineKeyboard(regions_keyboard, user[LANG]).get_keyboard()
    message = update.message.reply_text(text, reply_markup=inline_keyboard)

    state = FROM_REGION
    user_data[STATE] = state
    user_data[MESSAGE_ID] = message.message_id

    return REGION


def loop(icon, action, inline_keyboard):
    for row in inline_keyboard[2:]:
        for col in row:
            if col.callback_data != 'back':
                text = col.text.split(maxsplit=1)
                data = col.callback_data.split('_')
                col.text = f'{icon} {text[-1]}'
                col.callback_data = f'{data[0]}_{action}'


def region_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    region_id = callback_query.data
    user_data[user_data[STATE]] = int(region_id)

    if user[LANG] == LANGS[0]:
        text = "Qayerdan"
        text_2 = "Qayerga"
        text_3 = "(Tumanni tanlang)"
        text_4 = "Izoh: Siz, bir nechta tumanlarni tanlashingiz mumkin"

    if user[LANG] == LANGS[1]:
        text = "Откуда"
        text_2 = "Куда"
        text_3 = "(Выберите район)"
        text_4 = "Примечание:Вы можете выбрать несколько районов"

    if user[LANG] == LANGS[2]:
        text = "Қаердан"
        text_2 = "Қаерга"
        text_3 = "(Туманни танланг)"
        text_4 = "Изоҳ: Сиз, бир нечта туманларни танлашингиз мумкин"

    if user_data[STATE] == FROM_REGION:
        state = FROM_DISTRICT
    elif user_data[STATE] == TO_REGION:
        text = text_2
        state = TO_DISTRICT

    text = f'{text} {text_3}:\n\n' \
           f'🔅 {wrap_tags(text_4)}'
    inline_keyboard = InlineKeyboard(districts_selective_keyboard, user[LANG], data=region_id).get_keyboard()

    callback_query.answer()
    callback_query.edit_message_text(text, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)

    user_data[STATE] = state

    logger.info('user_data: %s', user_data)
    return DISTRICT


def district_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data

    if data == 'back':

        if user[LANG] == LANGS[0]:
            text = "Qayerdan"
            text_2 = "Qayerga"
            text_3 = "(Viloyatni tanlang)"

        if user[LANG] == LANGS[1]:
            text = "Откуда"
            text_2 = "Куда"
            text_3 = "(Выберите область)"

        if user[LANG] == LANGS[2]:
            text = "Қаердан"
            text_2 = "Қаерга"
            text_3 = "(Вилоятни танланг)"

        if user_data[STATE] == FROM_DISTRICT:
            state = FROM_REGION
        elif user_data[STATE] == TO_DISTRICT:
            text = text_2
            state = TO_REGION
        user_data.pop(state)

        text = f'{text} {text_3}:'
        inline_keyboard = InlineKeyboard(regions_keyboard, user[LANG]).get_keyboard()
        callback_query.edit_message_text(text, reply_markup=inline_keyboard)
        callback_query.answer()

        user_data[STATE] = state

        logger.info('user_data: %s', user_data)
        return REGION

    elif data == 'check_all':
        reply_markup = callback_query.message.reply_markup
        inline_keyboard = reply_markup.inline_keyboard

        try:
            icon = "✅"
            action = "checked"
            loop(icon, action, inline_keyboard)
            callback_query.edit_message_reply_markup(reply_markup)
        except TelegramError:
            icon = '☑'
            action = 'unchecked'
            loop(icon, action, inline_keyboard)
            callback_query.edit_message_reply_markup(reply_markup)

        callback_query.answer()

    elif data == 'save_checked':
        warning_icon = "⚠ "
        error_icon = "🛑"

        if user[LANG] == LANGS[0]:
            unchecked_text = "Birorta ham tuman tanlanmadi!\n\n" \
                             f"{warning_icon}Kamida bitta tumanni tanlang"
            text = "Saqlandi"
        if user[LANG] == LANGS[1]:
            unchecked_text = "Ни один район не был выбран!\n\n" \
                             f"{warning_icon}Выберите хотя бы один район"
            text = "Сохранено"
        if user[LANG] == LANGS[2]:
            unchecked_text = "Бирорта ҳам туман танланмади!\n\n" \
                             f"{warning_icon}Камида битта туманни танланг"
            text = "Сақланди"
        unchecked_text = f'{error_icon} {unchecked_text}!'
        checked_districts = []

        reply_markup = callback_query.message.reply_markup
        inline_keyboard = reply_markup.inline_keyboard
        for row in inline_keyboard[2:]:
            for col in row:
                if col.callback_data != 'back':
                    data = col.callback_data.split('_')
                    if data[-1] == 'checked':
                        checked_districts.append({
                            'district_id': int(data[0]),
                            'district_name': col.text.split(maxsplit=1)[-1]
                        })

        if len(checked_districts) == 0:
            callback_query.answer(unchecked_text, show_alert=True)
        else:
            alert_text = f'✅ {text}:\n'
            for district in checked_districts:
                alert_text += f"{district['district_name']}\n"

            # Throws TelegramError when message too long to display
            try:
                callback_query.answer(alert_text, show_alert=True)
            except TelegramError as e:
                callback_query.answer(text=f'✅ {text}', show_alert=True)

    elif data == 'ok':
        print(data)
    else:
        splited_data = data.split('_')
        district_id = splited_data[0]
        action = splited_data[-1]

        if action == 'checked':
            new_action = 'unchecked'
            new_icon = "☑"
        elif action == "unchecked":
            new_action = "checked"
            new_icon = "✅"
        stop = False

        reply_markup = callback_query.message.reply_markup
        inline_keyboard = reply_markup.inline_keyboard
        for row in inline_keyboard[2:]:
            for col in row:
                if col.callback_data == data:
                    text = col.text.split(maxsplit=1)
                    col.text = f'{new_icon} {text[-1]}'
                    col.callback_data = f'{district_id}_{new_action}'
                    stop = True
                    break
            if stop:
                break

        try:
            callback_query.edit_message_reply_markup(reply_markup)
        except TelegramError:
            pass
        callback_query.answer()


def activate_fallback(update: Update, context: CallbackContext):
    print('activate fallback')


activate_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(r"(Aktivlashtirish|Активация|Активлаштириш)$") &
                                 (~Filters.update.edited_message), activate_conversation_callback)],

    states={
        REGION: [CallbackQueryHandler(region_callback, pattern=r'^(\d+)$')],

        DISTRICT: [CallbackQueryHandler(district_callback,
                                        pattern=r'^(check_all|save_checked|back|\d+_(checked|unchecked)|ok)$')],

        # PASSENGERS: [CallbackQueryHandler(passenger_quantity_callback, pattern=r'^(\d+)$')],
        #
        # DATE: [CallbackQueryHandler(date_callback, pattern=r'^(now|\d+[-]\d+[-]\d+)$')],
        #
        # TIME: [CallbackQueryHandler(time_callback, pattern=r'^(back|next|\d+[:]00)$')],
        #
        # RECEIVER_CONTACT: [MessageHandler(
        #     Filters.contact | Filters.text & (~Filters.command) & (~Filters.update.edited_message),
        #     receiver_callback)],
        #
        # COMMENT: [
        #     CallbackQueryHandler(comment_callback, pattern=r'^no_comment$'),
        #     MessageHandler(Filters.text & (~Filters.command) & (~Filters.update.edited_message),
        #                    comment_callback)
        # ],
        #
        # CONFIRMATION: [CallbackQueryHandler(confirmation_callback, pattern='^(confirm|cancel)$')]
    },
    fallbacks=[MessageHandler(Filters.text & (~Filters.update.edited_message), activate_fallback)],

    persistent=True,

    name='activate_conversation'
)
