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
from DB import insert_data, get_user, get_car_baggage_status_car
from languages import LANGS
from layouts import get_active_driver_layout, get_comment_text
from globalvariables import *
from helpers import wrap_tags
from filters import phone_number_filter

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *
from inlinekeyboards.inlinekeyboardtypes import inline_keyboard_types

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

    text = f'{text}:'
    update.message.reply_text(update.message.text, reply_markup=ReplyKeyboardRemove())

    save_btn_icon = inline_keyboard_types[districts_selective_keyboard][1]['icon']
    save_btn_text = inline_keyboard_types[districts_selective_keyboard][1][f'text_{user[LANG]}']
    save_btn_text = f'{save_btn_icon} {save_btn_text}'
    save_btn_data = inline_keyboard_types[districts_selective_keyboard][1]['data']

    inline_keyboard = InlineKeyboard(regions_keyboard, user[LANG]).get_keyboard()
    inline_keyboard.inline_keyboard.append([InlineKeyboardButton(save_btn_text, callback_data=save_btn_data)])
    message = update.message.reply_text(text, reply_markup=inline_keyboard)

    state = FROM_REGION
    user_data[STATE] = state
    user_data[MESSAGE_ID] = message.message_id

    return REGION


def loop(icon, action, inline_keyboard):
    district_ids_list = []

    for row in inline_keyboard[1:]:
        for col in row:
            if col.callback_data != 'back':
                text = col.text.split(maxsplit=1)
                data = col.callback_data.split('_')
                col.text = f'{icon} {text[-1]}'
                col.callback_data = f'{data[0]}_{action}'
                district_ids_list.append(int(data[0]))

    return district_ids_list


def region_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data

    if user[LANG] == LANGS[0]:
        text = "Qayerdan"
        text_2 = "Qayerga"
        district_text = "(Tumanni tanlang)"
        region_text = "(Viloyatni tanlang)"
        note_text = "Izoh: Siz, bir nechta tumanlarni tanlashingiz mumkin"
        error_text = "Birorta ham tuman tanlanmadi.\n" \
                     "⚠ Iltimos, kamida bitta tumanni tanlang."
        empty_seats_text = "Bo'sh joylar sonini tanlang"
        alert_text = "Tanlangan tumanlar saqlandi"

    if user[LANG] == LANGS[1]:
        text = "Откуда"
        text_2 = "Куда"
        district_text = "(Выберите район)"
        region_text = "(Выберите область)"
        note_text = "Примечание:Вы можете выбрать несколько районов"
        error_text = "Ни один район не был выбран.\n" \
                     "⚠ Выберите хотя бы один район."
        empty_seats_text = "Выберите количество свободных мест"
        alert_text = "Выбранные районы сохранены"

    if user[LANG] == LANGS[2]:
        text = "Қаердан"
        text_2 = "Қаерга"
        district_text = "(Туманни танланг)"
        region_text = "(Вилоятни танланг)"
        note_text = "Изоҳ: Сиз, бир нечта туманларни танлашингиз мумкин"
        error_text = "Бирорта ҳам туман танланмади.\n" \
                     "⚠ Илтимос, камида битта туманни танланг."
        empty_seats_text = "Бўш жойлар сонини белгиланг"
        alert_text = "Танланган туманлар сақланди"

    if user_data[STATE] == FROM_REGION:
        state = FROM_DISTRICT
        key = 'from'
    elif user_data[STATE] == TO_REGION:
        state = TO_DISTRICT
        text = text_2
        key = 'to'

    if data == 'save_checked':

        if CHECKED not in user_data:
            user_data[CHECKED] = dict()
            user_data[CHECKED][key] = dict()

        if key not in user_data[CHECKED]:
            user_data[CHECKED][key] = dict()

        if not user_data[CHECKED][key]:
            error_text = f'🛑 {error_text}'
            callback_query.answer(error_text, show_alert=True)
            return

        if user_data[STATE] == FROM_REGION:
            state = TO_REGION
            return_state = REGION
            text = f'{text_2} {region_text}:'
            alert_text = f'✅ {alert_text}\n\n{text}'
            reply_markup = callback_query.message.reply_markup
            callback_query.edit_message_text(text, reply_markup=reply_markup)
            callback_query.answer(alert_text, show_alert=True)

        elif user_data[STATE] == TO_REGION:
            state = return_state = EMPTY_SEATS
            inline_keyboard = callback_query.message.reply_markup.from_row([
                InlineKeyboardButton('1', callback_data='1'),
                InlineKeyboardButton('2', callback_data='2'),
                InlineKeyboardButton('3', callback_data='3'),
                InlineKeyboardButton('4', callback_data='4'),
            ])
            text = f'{empty_seats_text}:'
            callback_query.edit_message_text(text, reply_markup=inline_keyboard)

        user_data[STATE] = state

        logger.info('user_data: %s', user_data)
        return return_state

    else:
        region_id = user_data[user_data[STATE]] = data = int(data)
        text = f'{text} {district_text}:\n\n' \
               f'🔅 {wrap_tags(note_text)}'

        if CHECKED in user_data:
            if key in user_data[CHECKED]:
                if region_id in user_data[CHECKED][key]:
                    data = {region_id: user_data[CHECKED][key][region_id]}
        inline_keyboard = InlineKeyboard(districts_selective_keyboard, user[LANG], data=data).get_keyboard()

        callback_query.edit_message_text(text, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)
        callback_query.answer()

        user_data[STATE] = state

        logger.info('user_data: %s', user_data)
        return DISTRICT


def district_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data

    if user[LANG] == LANGS[0]:
        text = "Qayerdan"
        text_2 = "Qayerga"
        text_3 = "(Viloyatni tanlang)"
        alert_text = "Barcha tumanlar tanlandi"
        alert_2_text = "tanlandi"
        alert_3_text = "olib tashlandi"

    if user[LANG] == LANGS[1]:
        text = "Откуда"
        text_2 = "Куда"
        text_3 = "(Выберите область)"
        alert_text = "Выбраны все районы"
        alert_2_text = "выбрано"
        alert_3_text = "удалено"

    if user[LANG] == LANGS[2]:
        text = "Қаердан"
        text_2 = "Қаерга"
        text_3 = "(Вилоятни танланг)"
        alert_text = "Барча туманлар танланди"
        alert_2_text = "танланди"
        alert_3_text = "олиб ташланди"

    if user_data[STATE] == FROM_DISTRICT:
        state = FROM_REGION
        region_id = user_data[state]
        key = 'from'
    elif user_data[STATE] == TO_DISTRICT:
        state = TO_REGION
        region_id = user_data[state]
        key = 'to'
        text = text_2

    if data == 'back':

        text = f'{text} {text_3}:'
        user_data.pop(state)

        save_btn_icon = inline_keyboard_types[districts_selective_keyboard][1]['icon']
        save_btn_text = inline_keyboard_types[districts_selective_keyboard][1][f'text_{user[LANG]}']
        save_btn_text = f'{save_btn_icon} {save_btn_text}'
        save_btn_data = inline_keyboard_types[districts_selective_keyboard][1]['data']

        inline_keyboard = InlineKeyboard(regions_keyboard, user[LANG]).get_keyboard()
        inline_keyboard.inline_keyboard.append([InlineKeyboardButton(save_btn_text, callback_data=save_btn_data)])
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
            alert_text = f'{icon} {alert_text}'
            district_ids_list = loop(icon, action, inline_keyboard)
            callback_query.edit_message_reply_markup(reply_markup)
            callback_query.answer(alert_text, show_alert=True)

            if CHECKED not in user_data:
                user_data[CHECKED] = dict()
                user_data[CHECKED][key] = dict()

            user_data[CHECKED][key].update({region_id: district_ids_list})

        except TelegramError:
            icon = '☑'
            action = 'unchecked'
            loop(icon, action, inline_keyboard)
            callback_query.edit_message_reply_markup(reply_markup)
            callback_query.answer()

            del user_data[CHECKED][key][region_id]

        logger.info('user_data: %s', user_data)

    else:

        splited_data = data.split('_')
        district_id = int(splited_data[0])
        action = splited_data[-1]

        if action == 'checked':
            new_action = 'unchecked'
            new_icon = "☑"
        elif action == "unchecked":
            new_action = "checked"
            new_icon = "✅"

        reply_markup = callback_query.message.reply_markup
        inline_keyboard = reply_markup.inline_keyboard
        for row in inline_keyboard[1:]:
            stop = False
            for col in row:
                if col.callback_data == data:
                    text = col.text.split(maxsplit=1)
                    col.text = f'{new_icon} {text[-1]}'
                    col.callback_data = f'{district_id}_{new_action}'
                    stop = True
                    break
            if stop:
                break

        # When user presses district button many times TelegramErrorn will be thrown
        # Error message: Message is not modified: specified new message content and reply markup are exactly
        # the same as a current content and reply markup of the message
        try:
            callback_query.edit_message_reply_markup(reply_markup)

            if CHECKED not in user_data:
                user_data[CHECKED] = dict()
                user_data[CHECKED][key] = dict()

            if action == 'unchecked':
                if key not in user_data[CHECKED]:
                    user_data[CHECKED][key] = {region_id: [district_id]}
                else:
                    if region_id in user_data[CHECKED][key]:
                        # List
                        user_data[CHECKED][key][region_id].append(district_id)
                    else:
                        user_data[CHECKED][key].update({region_id: [district_id]})
                alert = alert_2_text
            elif action == 'checked':
                # Remove district_id if exists in list
                user_data[CHECKED][key][region_id].remove(district_id)
                # If list empty delete the {refion_id: [districts_id]} whole dict
                if not user_data[CHECKED][key][region_id]:
                    del user_data[CHECKED][key][region_id]
                alert = alert_3_text

        except TelegramError:
            pass
        alert = f'{text[-1]} {alert}'
        callback_query.answer(alert)
        logger.info('user_data: %s', user_data)


def empty_seats_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query

    user_data[EMPTY_SEATS] = int(callback_query.data)

    if user[LANG] == LANGS[0]:
        text = "Pochta qabul qilasizmi"

    if user[LANG] == LANGS[1]:
        text = "Вы принимаете почту"

    if user[LANG] == LANGS[2]:
        text = "Почта қабул қиласизми"

    text = f'📦 {text}?'
    inline_keyboard = InlineKeyboard(yes_no_keyboard, user[LANG]).get_keyboard()
    callback_query.edit_message_text(text, reply_markup=inline_keyboard)
    callback_query.answer()

    user_data[STATE] = ASK_PARCEL

    logger.info('user_data: %s', user_data)
    return ASK_PARCEL


def ask_parcel_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    user_data[ASK_PARCEL] = True if callback_query.data == 'yes' else False

    text = get_comment_text(user[LANG])
    reply_markup = callback_query.message.reply_markup
    inline_keyboard = reply_markup.from_button(InlineKeyboardButton(text[1], callback_data='no_comment'))
    callback_query.edit_message_text(text[0], reply_markup=inline_keyboard)

    user_data[STATE] = COMMENT

    logger.info('user_data: %s', user_data)
    return COMMENT


def comment_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query

    user_data[COMMENT] = update.message.text if not callback_query else None

    if user[LANG] == LANGS[0]:
        text = "Jo'nash vaqtini yozib yuboring"
        example_text = "Misol uchun: bugun, kechasi 7larda, ertaga ertalab"

    if user[LANG] == LANGS[0]:
        text = "Запишите время отправления"
        example_text = "Например: сегодня,  в 7 вечера, завтра утром"

    if user[LANG] == LANGS[0]:
        text = "Жўнаш вақтини ёзиб юборинг"
        example_text = "Мисол учун: бугун, кечаси 7ларда, эртага эрталаб"

    text = f'{text}:\n\n' \
           f'{wrap_tags(example_text)}'

    callback_query.edit_message_text(text, parse_mode=ParseMode.HTML)

    user_data[STATE] = DEPARTURE_TIME

    logger.info('user_data: %s', user_data)
    return DEPARTURE_TIME


def departure_time_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    text = update.message.text
    user_data[DEPARTURE_TIME] = text
    user_data[FULLNAME] = user[FULLNAME]
    user_data[PHONE_NUMBER] = user[PHONE_NUMBER]
    data = get_car_baggage_status_car(user[ID])
    user_data[CAR_MODEL] = data[CAR_MODEL]
    user_data[BAGGAGE] = data[BAGGAGE]

    layout = get_active_driver_layout(user[LANG], data=user_data)
    inline_keyboard = InlineKeyboard(confirm_keyboard, user[LANG]).get_keyboard()
    message = update.message.reply_html(layout, reply_markup=inline_keyboard)

    user_data[STATE] = CONFIRMATION
    user_data[MESSAGE_ID] = message.message_id

    logger.info('user_data: %s', user_data)
    return CONFIRMATION


def confirmation_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_quary = update.callback_query
    data = callback_quary.data
    print(data)


def activate_fallback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    text = update.message.text

    if text == '/start' or text == '/menu' or text == '/cancel':

        if user[LANG] == LANGS[0]:
            text = "Aktivlashtirish bekor qilindi"
        if user[LANG] == LANGS[1]:
            text = "Активация отменена"
        if user[LANG] == LANGS[2]:
            text = "Активлаштириш бекор қилинди"

        text = f'‼ {text}!'
        keyboard = driver_keyboard if text == '/cancel' else main_menu_keyboard
        reply_keyboard = ReplyKeyboard(keyboard, user[LANG]).get_keyboard()
        update.message.reply_text(text, reply_markup=reply_keyboard)

        if MESSAGE_ID in user_data:
            try:
                context.bot.delete_message(user[TG_ID], user_data[MESSAGE_ID])
            except TelegramError:
                try:
                    context.bot.edit_message_reply_markup(user[TG_ID], user_data[MESSAGE_ID])
                except TelegramError:
                    pass

        user_data.clear()
        return ConversationHandler.END

    else:

        if user[LANG] == LANGS[0]:
            text = "Hozir aktivlashtirish bo'limidasiz.\n\n" \
                   "Aktivlashtirishni to'xtatish uchun /cancel ni bosing.\n\n" \
                   "Bosh menyuga qaytish uchun /menu ni bosing"

        if user[LANG] == LANGS[1]:
            text = "Вы сейчас в разделе активации.\n\n" \
                   "Нажмите /cancel, чтобы остановить активацию.\n\n" \
                   "Нажмите /menu, чтобы вернуться в главное меню."

        if user[LANG] == LANGS[2]:
            text = "Ҳозир сиз активлаштириш бўлимидасиз.\n\n" \
                   "Активлаштиришни тўхтатиш учун /cancel ни босинг.\n\n" \
                   "Бош менюга қайтиш учун /menu ни босинг."

        update.message.reply_text(text)
        return


activate_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(r"(Aktivlashtirish|Активация|Активлаштириш)$") &
                                 (~Filters.update.edited_message), activate_conversation_callback)],

    states={
        REGION: [CallbackQueryHandler(region_callback, pattern=r'^(\d+|save_checked)$')],

        DISTRICT: [CallbackQueryHandler(district_callback, pattern=r'^(check_all|back|\d+_(checked|unchecked))$')],

        EMPTY_SEATS: [CallbackQueryHandler(empty_seats_callback, pattern=r'^\d+$')],

        ASK_PARCEL: [CallbackQueryHandler(ask_parcel_callback, pattern=r'^(yes|no)$')],

        COMMENT: [
            CallbackQueryHandler(comment_callback, pattern=r'^no_comment$'),
            MessageHandler(Filters.text & (~Filters.command) & (~Filters.update.edited_message), comment_callback)
        ],

        DEPARTURE_TIME: [MessageHandler(Filters.text & (~Filters.command) & (~Filters.update.edited_message),
                                        departure_time_callback)],

        CONFIRMATION: [CallbackQueryHandler(confirmation_callback, pattern='^(confirm|cancel)$')]
    },
    fallbacks=[MessageHandler(Filters.text & (~Filters.update.edited_message), activate_fallback)],

    persistent=True,

    name='activate_conversation'
)
