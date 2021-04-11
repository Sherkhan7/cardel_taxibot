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
from DB import (
    get_user,
    get_driver_and_car_data,
    get_active_driver_by_driver_id,
    update_active_driver_comment,
    update_active_driver_empty_seats,
    update_active_driver_ask_parcel,
    update_active_driver_departure_time,
    update_active_driver_from_or_to,
)
from languages import LANGS
from layouts import get_active_driver_layout, get_comment_text
from globalvariables import *
from helpers import wrap_tags

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *
from replykeyboards.replykeyboardtypes import reply_keyboard_types

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *
from inlinekeyboards.inlinekeyboardtypes import inline_keyboard_types

import logging
import json
import datetime

logger = logging.getLogger()

EDIT_EMPTY_SEATS, EDIT_DISTRICT, EDIT_REGION, EDIT_ASK_PARCEL, EDIT_DATE, EDIT_TIME, EDIT_COMMENT = \
    ('edit_empty_seats', 'edit_district', 'edit_region', 'edit_ask_parcel', 'edit_date', 'edit_time', 'edit_comment')


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


def get_edited_alert(lang):
    if lang == LANGS[0]:
        alert_text = "Tahrirlandi"
    if lang == LANGS[1]:
        alert_text = "Отредактировано"
    if lang == LANGS[2]:
        alert_text = "Таҳрирланди"

    return '✅ ' + alert_text


def set_data(user, driver_and_car_data, active_driver_data):
    data = dict()
    data[CHECKED] = dict()
    data[FULLNAME] = user[FULLNAME]
    data[PHONE_NUMBER] = user[PHONE_NUMBER]
    data[CAR_MODEL] = driver_and_car_data[CAR_MODEL]
    data[BAGGAGE] = driver_and_car_data[BAGGAGE]
    data[CHECKED]['from'] = json.loads(active_driver_data['from_'])
    data[CHECKED]['to'] = json.loads(active_driver_data['to_'])
    data[EMPTY_SEATS] = active_driver_data[EMPTY_SEATS]
    data[ASK_PARCEL] = active_driver_data[ASK_PARCEL]
    data[COMMENT] = active_driver_data[COMMENT]
    departure_time = active_driver_data[DEPARTURE_TIME].split()
    data[DATE] = departure_time[0]
    data[TIME] = departure_time[-1]

    return data


def edit_conversation_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    update.message.reply_text(update.message.text, reply_markup=ReplyKeyboardRemove())

    driver_and_car_data = get_driver_and_car_data(user[ID])
    active_driver_data = get_active_driver_by_driver_id(driver_and_car_data[ID])
    data = set_data(user, driver_and_car_data, active_driver_data)
    label = reply_keyboard_types[active_driver_keyboard][0][f'text_{user[LANG]}']
    layout = get_active_driver_layout(user[LANG], data=data, label=f'[{label}]')
    inline_keyboard = InlineKeyboard(edit_keyboard, user[LANG]).get_keyboard()
    message = update.message.reply_html(layout, reply_markup=inline_keyboard)

    user_data[STATE] = CHOOSE_EDITING
    user_data[MESSAGE_ID] = message.message_id

    return CHOOSE_EDITING


def choose_editing_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    action = callback_query.data.split('_', maxsplit=1)[-1]
    back_btn_icon = inline_keyboard_types[back_next_keyboard][0]['icon']
    back_btn_text = inline_keyboard_types[back_next_keyboard][0][f'text_{user[LANG]}']
    back_btn_text = f'{back_btn_icon} {back_btn_text}'
    back_btn_data = inline_keyboard_types[back_next_keyboard][0]['data']

    if action == 'from' or action == 'to':
        if user[LANG] == LANGS[0]:
            text = "Qayerdan"
            text_2 = "Qayerga"
            region_text = "(Viloyatni tanlang)"

        if user[LANG] == LANGS[1]:
            text = "Откуда"
            text_2 = "Куда"
            region_text = "(Выберите область)"

        if user[LANG] == LANGS[2]:
            text = "Қаердан"
            text_2 = "Қаерга"
            region_text = "(Вилоятни танланг)"

        if action == 'from':
            state = 'edit_from_region'
        else:
            state = 'edit_to_region'
            text = text_2
        text = f'{text} {region_text}:'
        save_btn_icon = inline_keyboard_types[districts_selective_keyboard][1]['icon']
        save_btn_text = inline_keyboard_types[districts_selective_keyboard][1][f'text_{user[LANG]}']
        save_btn_text = f'{save_btn_icon} {save_btn_text}'
        save_btn_data = inline_keyboard_types[districts_selective_keyboard][1]['data']

        inline_keyboard = InlineKeyboard(regions_keyboard, user[LANG]).get_keyboard()
        inline_keyboard.inline_keyboard.append([InlineKeyboardButton(save_btn_text, callback_data=save_btn_data)])
        inline_keyboard.inline_keyboard.append([InlineKeyboardButton(back_btn_text, callback_data=back_btn_data)])
        callback_query.edit_message_text(text, reply_markup=inline_keyboard)

        user_data[STATE] = state

        logger.info('user_data: %s', user_data)
        return EDIT_REGION

    elif action == EMPTY_SEATS:

        if user[LANG] == LANGS[0]:
            empty_seats_text = "Bo'sh joylar sonini tanlang"
        if user[LANG] == LANGS[1]:
            empty_seats_text = "Выберите количество свободных мест"
        if user[LANG] == LANGS[2]:
            empty_seats_text = "Бўш жойлар сонини белгиланг"
        text = f'{empty_seats_text}:'
        inline_keyboard = callback_query.message.reply_markup.from_row([
            InlineKeyboardButton('1', callback_data='1'),
            InlineKeyboardButton('2', callback_data='2'),
            InlineKeyboardButton('3', callback_data='3'),
            InlineKeyboardButton('4', callback_data='4'),
        ])
        inline_keyboard.inline_keyboard.append([InlineKeyboardButton(back_btn_text, callback_data=back_btn_data)])
        callback_query.edit_message_text(text, reply_markup=inline_keyboard)

        user_data[STATE] = EDIT_EMPTY_SEATS
        return EDIT_EMPTY_SEATS

    elif action == ASK_PARCEL:

        if user[LANG] == LANGS[0]:
            text = "Pochta qabul qilasizmi"
        if user[LANG] == LANGS[1]:
            text = "Вы принимаете почту"
        if user[LANG] == LANGS[2]:
            text = "Почта қабул қиласизми"
        text = f'📦 {text}?'
        inline_keyboard = InlineKeyboard(yes_no_keyboard, user[LANG]).get_keyboard()
        inline_keyboard.inline_keyboard.append([InlineKeyboardButton(back_btn_text, callback_data=back_btn_data)])
        callback_query.edit_message_text(text, reply_markup=inline_keyboard)

        user_data[STATE] = EDIT_ASK_PARCEL
        return EDIT_ASK_PARCEL

    elif action == DATETIME:

        if user[LANG] == LANGS[0]:
            text = "Ketish kunini belgilang"
        if user[LANG] == LANGS[1]:
            text = "Установите дату отъезда"
        if user[LANG] == LANGS[2]:
            text = "Кетиш кунини белгиланг"
        text = f'{text}:'
        inline_keyboard = InlineKeyboard(dates_keyboard, user[LANG]).get_keyboard()
        inline_keyboard.inline_keyboard.append([InlineKeyboardButton(back_btn_text, callback_data=back_btn_data)])
        callback_query.edit_message_text(text, reply_markup=inline_keyboard)

        user_data[STATE] = EDIT_DATE
        return EDIT_DATE

    elif action == COMMENT:
        text = get_comment_text(user[LANG])

        inline_keyboard = callback_query.message.reply_markup
        inline_keyboard = inline_keyboard.from_column([
            InlineKeyboardButton(text[1], callback_data='no_comment'),
            InlineKeyboardButton(back_btn_text, callback_data=back_btn_data)
        ])
        callback_query.edit_message_text(text[0], reply_markup=inline_keyboard)

        user_data[STATE] = EDIT_COMMENT
        return EDIT_COMMENT

    callback_query.answer()


def edit_region_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    driver_and_car_data = get_driver_and_car_data(user[ID])
    callback_query = update.callback_query
    data = callback_query.data

    if user[LANG] == LANGS[0]:
        text = "Qayerdan"
        text_2 = "Qayerga"
        district_text = "(Tumanni tanlang)"
        note_text = "Izoh: Siz, bir nechta tumanlarni tanlashingiz mumkin"
        error_text = "Birorta ham tuman tanlanmadi.\n" \
                     "⚠ Iltimos, kamida bitta tumanni tanlang."

    if user[LANG] == LANGS[1]:
        text = "Откуда"
        text_2 = "Куда"
        district_text = "(Выберите район)"
        note_text = "Примечание: Вы можете выбрать несколько районов"
        error_text = "Ни один район не был выбран.\n" \
                     "⚠ Выберите хотя бы один район."

    if user[LANG] == LANGS[2]:
        text = "Қаердан"
        text_2 = "Қаерга"
        district_text = "(Туманни танланг)"
        note_text = "Изоҳ: Сиз, бир нечта туманларни танлашингиз мумкин"
        error_text = "Бирорта ҳам туман танланмади.\n" \
                     "⚠ Илтимос, камида битта туманни танланг."

    if user_data[STATE] == 'edit_from_region':
        state = 'edit_from_district'
        key = 'from'
    elif user_data[STATE] == 'edit_to_region':
        state = 'edit_to_district'
        text = text_2
        key = 'to'

    if data == 'save_checked':

        if CHECKED not in user_data:
            user_data[CHECKED] = dict()
            user_data[CHECKED][key] = dict()

        elif key not in user_data[CHECKED]:
            user_data[CHECKED][key] = dict()

        if not user_data[CHECKED][key]:
            error_text = f'🛑 {error_text}'
            callback_query.answer(error_text, show_alert=True)
            return

        new_json = json.dumps(user_data[CHECKED][key])
        update_active_driver_from_or_to(key, new_json, driver_and_car_data[ID])
        callback_query.answer(get_edited_alert(user[LANG]), show_alert=True)

    elif data != 'back':
        region_id = user_data[user_data[STATE]] = data = int(data)
        text = f'{text} {district_text}:\n\n' \
               f'🔅 {wrap_tags(note_text)}'

        if CHECKED in user_data and key in user_data[CHECKED] and region_id in user_data[CHECKED][key]:
            data = {region_id: user_data[CHECKED][key][region_id]}
        inline_keyboard = InlineKeyboard(districts_selective_keyboard, user[LANG], data=data).get_keyboard()

        callback_query.edit_message_text(text, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)
        callback_query.answer()

        user_data[STATE] = state

        logger.info('user_data: %s', user_data)
        return EDIT_DISTRICT

    active_driver_data = get_active_driver_by_driver_id(driver_and_car_data[ID])
    data = set_data(user, driver_and_car_data, active_driver_data)
    label = reply_keyboard_types[active_driver_keyboard][0][f'text_{user[LANG]}']
    layout = get_active_driver_layout(user[LANG], data=data, label=f'[{label}]')
    inline_keyboard = InlineKeyboard(edit_keyboard, user[LANG]).get_keyboard()
    callback_query.edit_message_text(layout, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)

    user_data[STATE] = CHOOSE_EDITING
    if CHECKED in user_data:
        user_data.pop(CHECKED)

    logger.info('user_data: %s', user_data)
    return CHOOSE_EDITING


def edit_district_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data

    if user[LANG] == LANGS[0]:
        text = "Qayerdan"
        text_2 = "Qayerga"
        region_text = "(Viloyatni tanlang)"
        all_alert_text = "Barcha tumanlar tanlandi"
        checked_alert_text = "tanlandi"
        unchecked_alert_text = "olib tashlandi"

    if user[LANG] == LANGS[1]:
        text = "Откуда"
        text_2 = "Куда"
        region_text = "(Выберите область)"
        all_alert_text = "Выбраны все районы"
        checked_alert_text = "выбрано"
        unchecked_alert_text = "удалено"

    if user[LANG] == LANGS[2]:
        text = "Қаердан"
        text_2 = "Қаерга"
        region_text = "(Вилоятни танланг)"
        all_alert_text = "Барча туманлар танланди"
        checked_alert_text = "танланди"
        unchecked_alert_text = "олиб ташланди"

    if user_data[STATE] == 'edit_from_district':
        state = 'edit_from_region'
        key = 'from'
    elif user_data[STATE] == 'edit_to_district':
        state = 'edit_to_region'
        key = 'to'
        text = text_2
    region_id = user_data[state]

    if data == 'back':

        text = f'{text} {region_text}:'
        user_data.pop(state)

        save_btn_icon = inline_keyboard_types[districts_selective_keyboard][1]['icon']
        save_btn_text = inline_keyboard_types[districts_selective_keyboard][1][f'text_{user[LANG]}']
        save_btn_text = f'{save_btn_icon} {save_btn_text}'
        save_btn_data = inline_keyboard_types[districts_selective_keyboard][1]['data']

        back_btn_icon = inline_keyboard_types[back_next_keyboard][0]['icon']
        back_btn_text = inline_keyboard_types[back_next_keyboard][0][f'text_{user[LANG]}']
        back_btn_text = f'{back_btn_icon} {back_btn_text}'
        back_btn_data = inline_keyboard_types[back_next_keyboard][0]['data']

        inline_keyboard = InlineKeyboard(regions_keyboard, user[LANG]).get_keyboard()
        inline_keyboard.inline_keyboard.append([InlineKeyboardButton(save_btn_text, callback_data=save_btn_data)])
        inline_keyboard.inline_keyboard.append([InlineKeyboardButton(back_btn_text, callback_data=back_btn_data)])
        callback_query.edit_message_text(text, reply_markup=inline_keyboard)
        callback_query.answer()

        user_data[STATE] = state

        logger.info('user_data: %s', user_data)
        return EDIT_REGION

    elif data == 'check_all':
        reply_markup = callback_query.message.reply_markup
        inline_keyboard = reply_markup.inline_keyboard

        try:
            icon = "✅"
            action = "checked"
            all_alert_text = f'{icon} {all_alert_text}'
            district_ids_list = loop(icon, action, inline_keyboard)
            callback_query.edit_message_reply_markup(reply_markup)
            callback_query.answer(all_alert_text)

            if CHECKED not in user_data:
                user_data[CHECKED] = dict()
                user_data[CHECKED][key] = dict()

            elif key not in user_data[CHECKED]:
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
        return

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
        stop = False
        for row in inline_keyboard[1:]:
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

            elif key not in user_data[CHECKED]:
                user_data[CHECKED][key] = dict()

            if new_action == 'checked':

                if not user_data[CHECKED][key]:
                    user_data[CHECKED][key] = {region_id: [district_id]}
                elif region_id in user_data[CHECKED][key]:
                    # List
                    user_data[CHECKED][key][region_id].append(district_id)
                else:
                    user_data[CHECKED][key].update({region_id: [district_id]})
                alert = checked_alert_text

            elif new_action == 'unchecked':
                # Remove district_id if exists in list
                user_data[CHECKED][key][region_id].remove(district_id)
                # If list is empty delete the {region_id: [districts_id]} whole dict
                if not user_data[CHECKED][key][region_id]:
                    del user_data[CHECKED][key][region_id]
                alert = unchecked_alert_text

        except TelegramError:
            pass

        alert = f'{text[-1]} {alert}'
        callback_query.answer(alert)
        logger.info('user_data: %s', user_data)
        return


def edit_empty_seats_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    driver_and_car_data = get_driver_and_car_data(user[ID])
    callback_query = update.callback_query

    if callback_query.data != 'back':
        update_active_driver_empty_seats(int(callback_query.data), driver_and_car_data[ID])
        callback_query.answer(get_edited_alert(user[LANG]), show_alert=True)

    active_driver_data = get_active_driver_by_driver_id(driver_and_car_data[ID])
    data = set_data(user, driver_and_car_data, active_driver_data)
    label = reply_keyboard_types[active_driver_keyboard][0][f'text_{user[LANG]}']
    layout = get_active_driver_layout(user[LANG], data=data, label=f'[{label}]')
    inline_keyboard = InlineKeyboard(edit_keyboard, user[LANG]).get_keyboard()
    callback_query.edit_message_text(layout, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)

    user_data[STATE] = CHOOSE_EDITING
    return CHOOSE_EDITING


def edit_ask_parcel_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    driver_and_car_data = get_driver_and_car_data(user[ID])
    callback_query = update.callback_query

    if callback_query.data != 'back':
        new_answer = True if callback_query.data == 'yes' else False
        update_active_driver_ask_parcel(new_answer, driver_and_car_data[ID])
        callback_query.answer(get_edited_alert(user[LANG]), show_alert=True)

    active_driver_data = get_active_driver_by_driver_id(driver_and_car_data[ID])
    data = set_data(user, driver_and_car_data, active_driver_data)
    label = reply_keyboard_types[active_driver_keyboard][0][f'text_{user[LANG]}']
    layout = get_active_driver_layout(user[LANG], data=data, label=f'[{label}]')
    inline_keyboard = InlineKeyboard(edit_keyboard, user[LANG]).get_keyboard()
    callback_query.edit_message_text(layout, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)

    user_data[STATE] = CHOOSE_EDITING
    return CHOOSE_EDITING


def edit_date_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    driver_and_car_data = get_driver_and_car_data(user[ID])
    callback_query = update.callback_query
    data = callback_query.data

    if data == 'now':
        new_departure = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        update_active_driver_departure_time(new_departure, driver_and_car_data[ID])
        callback_query.answer(get_edited_alert(user[LANG]), show_alert=True)

    elif data != 'back':

        user_data['new_date'] = data

        if user[LANG] == LANGS[0]:
            text = "Soatni belgilang"
        if user[LANG] == LANGS[1]:
            text = "Выберите время"
        if user[LANG] == LANGS[2]:
            text = "Соатни белгиланг"
        text = f'{text}:'
        inline_keyboard = InlineKeyboard(times_keyboard, user[LANG],
                                         data={'begin': 6, 'end': 17, 'undefined': True}).get_keyboard()
        callback_query.edit_message_text(text, reply_markup=inline_keyboard)

        user_data[STATE] = EDIT_TIME

        return EDIT_TIME

    active_driver_data = get_active_driver_by_driver_id(driver_and_car_data[ID])
    data = set_data(user, driver_and_car_data, active_driver_data)
    label = reply_keyboard_types[active_driver_keyboard][0][f'text_{user[LANG]}']
    layout = get_active_driver_layout(user[LANG], data=data, label=f'[{label}]')
    inline_keyboard = InlineKeyboard(edit_keyboard, user[LANG]).get_keyboard()
    callback_query.edit_message_text(layout, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)

    user_data[STATE] = CHOOSE_EDITING
    return CHOOSE_EDITING


def edit_time_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    driver_and_car_data = get_driver_and_car_data(user[ID])
    callback_query = update.callback_query
    data = callback_query.data

    if data == 'next' or data == 'back':

        if data == 'next':
            inline_keyboard = InlineKeyboard(times_keyboard, user[LANG],
                                             data={'begin': 18, 'end': 29, 'undefined': True}).get_keyboard()
        if data == 'back':
            inline_keyboard = InlineKeyboard(times_keyboard, user[LANG],
                                             data={'begin': 6, 'end': 17, 'undefined': True}).get_keyboard()

        callback_query.edit_message_reply_markup(inline_keyboard)
        callback_query.answer()

        return

    else:
        new_departure = f'{user_data["new_date"]} {data}'
        update_active_driver_departure_time(new_departure, driver_and_car_data[ID])
        callback_query.answer(get_edited_alert(user[LANG]), show_alert=True)
        if 'new_date' in user_data:
            user_data.pop('new_date')

        active_driver_data = get_active_driver_by_driver_id(driver_and_car_data[ID])
        data = set_data(user, driver_and_car_data, active_driver_data)
        label = reply_keyboard_types[active_driver_keyboard][0][f'text_{user[LANG]}']
        layout = get_active_driver_layout(user[LANG], data=data, label=f'[{label}]')
        inline_keyboard = InlineKeyboard(edit_keyboard, user[LANG]).get_keyboard()
        callback_query.edit_message_text(layout, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)

        user_data[STATE] = CHOOSE_EDITING
        return CHOOSE_EDITING


def edit_comment_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    driver_and_car_data = get_driver_and_car_data(user[ID])
    callback_query = update.callback_query

    if callback_query is None:
        update_active_driver_comment(update.message.text, driver_and_car_data[ID])
        active_driver_data = get_active_driver_by_driver_id(driver_and_car_data[ID])

        context.bot.edit_message_reply_markup(user[TG_ID], user_data[MESSAGE_ID])

        layout = get_active_driver_layout(user[LANG], data=set_data(user, driver_and_car_data, active_driver_data))
        inline_keyboard = InlineKeyboard(edit_keyboard, user[LANG]).get_keyboard()
        message = update.message.reply_html(layout, reply_markup=inline_keyboard)
        user_data[MESSAGE_ID] = message.message_id

        user_data[STATE] = CHOOSE_EDITING
        return CHOOSE_EDITING

    elif callback_query.data == 'no_comment':
        update_active_driver_comment(None, driver_and_car_data[ID])
        callback_query.answer(get_edited_alert(user[LANG]), show_alert=True)

    active_driver_data = get_active_driver_by_driver_id(driver_and_car_data[ID])
    data = set_data(user, driver_and_car_data, active_driver_data)
    label = reply_keyboard_types[active_driver_keyboard][0][f'text_{user[LANG]}']
    layout = get_active_driver_layout(user[LANG], data=data, label=f'[{label}]')
    inline_keyboard = InlineKeyboard(edit_keyboard, user[LANG]).get_keyboard()
    callback_query.edit_message_text(layout, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)

    user_data[STATE] = CHOOSE_EDITING
    return CHOOSE_EDITING


def edit_fallback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    text = update.message.text

    if text == '/start' or text == '/menu' or text == '/cancel':

        keyboard = active_driver_keyboard if text == '/cancel' else main_menu_keyboard

        if user[LANG] == LANGS[0]:
            text = "Tahrirlash bekor qilindi"

        if user[LANG] == LANGS[1]:
            text = "Редактирование отменено"

        if user[LANG] == LANGS[2]:
            text = "Таҳрирлаш бекор қилинди"

        text = f'‼ {text}!'
        reply_keyboard = ReplyKeyboard(keyboard, user[LANG]).get_keyboard()
        update.message.reply_text(text, reply_markup=reply_keyboard)

        if MESSAGE_ID in user_data:
            try:
                context.bot.delete_message(user[TG_ID], user_data[MESSAGE_ID])
            except TelegramError:
                context.bot.edit_message_reply_markup(user[TG_ID], user_data[MESSAGE_ID])

        user_data.clear()
        return ConversationHandler.END

    else:

        if user[LANG] == LANGS[0]:
            text = "Hozir siz tahrirlash bo'limidasiz\n\n" \
                   "Tahrirlashni to'xtatish uchun /cancel ni bosing"

        if user[LANG] == LANGS[1]:
            text = "Вы сейчас в разделе редактирования\n\n" \
                   "Нажмите /cancel, чтобы остановить редактирование"

        if user[LANG] == LANGS[2]:
            text = "Ҳозир сиз таҳрирлаш бўлимидасиз\n\n" \
                   "Таҳрирлашни тўхтатиш учун /cancel ни босинг"

        update.message.reply_text(text)
        return


edit_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(r"(Tahrirlash|Редактировать|Таҳрирлаш)$") &
                                 (~Filters.update.edited_message), edit_conversation_callback)],

    states={
        CHOOSE_EDITING: [CallbackQueryHandler(choose_editing_callback, pattern=r'^edit_\w+$')],

        EDIT_REGION: [CallbackQueryHandler(edit_region_callback, pattern=r'^(\d+|save_checked|back)$')],

        EDIT_DISTRICT: [
            CallbackQueryHandler(edit_district_callback, pattern=r'^(check_all|back|\d+_(checked|unchecked))$')],

        EDIT_EMPTY_SEATS: [CallbackQueryHandler(edit_empty_seats_callback, pattern=r'^(\d+|back)$')],

        EDIT_ASK_PARCEL: [CallbackQueryHandler(edit_ask_parcel_callback, pattern=r'^(yes|no|back)$')],

        EDIT_DATE: [CallbackQueryHandler(edit_date_callback, pattern=r'^(now|\d+[-]\d+[-]\d+|back)$')],

        EDIT_TIME: [CallbackQueryHandler(edit_time_callback, pattern=r'^(back|next|\d+[:]00|undefined)$')],

        EDIT_COMMENT: [
            CallbackQueryHandler(edit_comment_callback, pattern=r'^(no_comment|back)$'),
            MessageHandler(Filters.text & (~Filters.command) & (~Filters.update.edited_message), edit_comment_callback)
        ],
    },
    fallbacks=[MessageHandler(Filters.text & (~Filters.update.edited_message), edit_fallback)],

    persistent=True,

    name='edit_conversation'
)
