import logging
import ujson
import datetime
import re

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
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
from DB import *
from languages import LANGS
from layouts import get_active_driver_layout, get_comment_text
from globalvariables import *
from helpers import *

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *
from replykeyboards.replykeyboardtypes import reply_keyboard_types

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *
from inlinekeyboards.inlinekeyboardtypes import inline_keyboard_types

logger = logging.getLogger()


def get_edited_alert(lang):
    if lang == LANGS[0]:
        alert_text = "Tahrirlandi"
    if lang == LANGS[1]:
        alert_text = "Отредактировано"
    if lang == LANGS[2]:
        alert_text = "Таҳрирланди"

    return '✅ ' + alert_text


def edit_conversation_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    back_btn_icon = reply_keyboard_types[settings_keyboard][2]['icon']
    back_btn_text = reply_keyboard_types[settings_keyboard][2][f'text_{user[LANG]}']
    back_btn_text = f'{back_btn_icon} {back_btn_text}'

    reply_keyboard = ReplyKeyboardMarkup([
        [KeyboardButton(back_btn_text)],
    ], resize_keyboard=True)
    update.message.reply_text(update.message.text, reply_markup=reply_keyboard)

    if user[LANG] == LANGS[0]:
        text = "Hozir siz aktiv holatda emassiz.\n\n" \
               "Aktiv holatga o'tish ucun 🔄 Aktivlashtirish tugmasini bosing."
        btn_1_text = "Tahrirlash"
        btn_2_text = "O'chirish"

    if user[LANG] == LANGS[1]:
        text = "Вы в настоящее время не активны.\n\n" \
               "Нажмите кнопку 🔄 Активировать, чтобы перейти в активный режим."
        btn_1_text = "Редактировать"
        btn_2_text = "Удалить"

    if user[LANG] == LANGS[2]:
        text = "Ҳозир сиз актив ҳолатда эмассиз.\n\n" \
               "Актив ҳолатга ўтиш уcун 🔄 Активлаштириш тугмасини босинг."
        btn_1_text = "Таҳрирлаш"
        btn_2_text = "Ўчириш"

    active_driver_data = get_active_driver_by_user_id(user[ID])

    if active_driver_data is None:
        reply_keyboard = ReplyKeyboard(driver_keyboard, user[LANG]).get_keyboard()
        update.message.reply_text(text, reply_markup=reply_keyboard)

        return ConversationHandler.END

    driver_and_car_data = get_driver_and_car_data(user[ID])
    data = set_data(user, driver_and_car_data, active_driver_data)
    label = reply_keyboard_types[active_driver_keyboard][0][f'text_{user[LANG]}']
    active_driver_layout = get_active_driver_layout(user[LANG], data, label)

    inline_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f'📝 {btn_1_text}', callback_data='editing')],
        [InlineKeyboardButton(f'❌ {btn_2_text}', callback_data='delete')],
    ])
    message = update.message.reply_html(active_driver_layout, reply_markup=inline_keyboard)

    user_data[STATE] = CHOOSE_EDITING
    user_data[MESSAGE_ID] = message.message_id

    return CHOOSE_EDITING


def choose_editing_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query

    # This try/except used to catch `telegram.error.BadRequest:
    # Query is too old and response timeout expired or query id is invalid`
    try:
        callback_query.answer()
    except TelegramError:
        pass

    if user[LANG] == LANGS[0]:
        from_text = "Qayerdan"
        to_text = "Qayerga"
        region_text = "(Viloyatni tanlang)"
        empty_seats_text = "Bo'sh joylar sonini tanlang"
        ask_parcel_text = "Pochta qabul qilasizmi"
        date_text = "Ketish kunini belgilang"
        edit_btn_text = "Tahrirlash"
        delete_btn_text = "O'chirish"
        alert_text = "Aktiv holat o'chirildi"

    if user[LANG] == LANGS[1]:
        from_text = "Откуда"
        to_text = "Куда"
        region_text = "(Выберите область)"
        empty_seats_text = "Выберите количество свободных мест"
        ask_parcel_text = "Вы принимаете почту"
        date_text = "Установите дату отъезда"
        edit_btn_text = "Редактировать"
        delete_btn_text = "Удалить"
        alert_text = "Активный режим отключен"

    if user[LANG] == LANGS[2]:
        from_text = "Қаердан"
        to_text = "Қаерга"
        region_text = "(Вилоятни танланг)"
        empty_seats_text = "Бўш жойлар сонини белгиланг"
        ask_parcel_text = "Почта қабул қиласизми"
        date_text = "Кетиш кунини белгиланг"
        edit_btn_text = "Таҳрирлаш"
        delete_btn_text = "Ўчириш"
        alert_text = "Актив ҳолат ўчирилди"

    empty_seats_text = f'{empty_seats_text}:'
    date_text = f'{date_text}:'
    ask_parcel_text = f'📦 {ask_parcel_text}?'

    back_btn_icon = inline_keyboard_types[back_next_keyboard][0]['icon']
    back_btn_text = inline_keyboard_types[back_next_keyboard][0][f'text_{user[LANG]}']
    back_btn_text = f'{back_btn_icon} {back_btn_text}'
    back_btn_data = inline_keyboard_types[back_next_keyboard][0]['data']

    if callback_query.data == 'edit_from' or callback_query.data == 'edit_to':

        if callback_query.data == 'edit_from':
            state = 'edit_from_region'
            text = from_text
        else:
            state = 'edit_to_region'
            text = to_text

        text = f'{text} {region_text}:'
        inline_keyboard = InlineKeyboard(regions_keyboard, user[LANG], data=True).get_keyboard()
        inline_keyboard.inline_keyboard.append([InlineKeyboardButton(back_btn_text, callback_data=back_btn_data)])
        callback_query.edit_message_text(text, reply_markup=inline_keyboard)

        user_data[STATE] = state

        return EDIT_REGION

    elif callback_query.data == EDIT_EMPTY_SEATS:

        inline_keyboard = callback_query.message.reply_markup.from_row([
            InlineKeyboardButton('1', callback_data='1'),
            InlineKeyboardButton('2', callback_data='2'),
            InlineKeyboardButton('3', callback_data='3'),
            InlineKeyboardButton('4', callback_data='4'),
        ])
        inline_keyboard.inline_keyboard.append([InlineKeyboardButton(back_btn_text, callback_data=back_btn_data)])
        callback_query.edit_message_text(empty_seats_text, reply_markup=inline_keyboard)

        user_data[STATE] = EDIT_EMPTY_SEATS

        return EDIT_EMPTY_SEATS

    elif callback_query.data == EDIT_ASK_PARCEL:

        inline_keyboard = InlineKeyboard(yes_no_keyboard, user[LANG]).get_keyboard()
        inline_keyboard.inline_keyboard.append([InlineKeyboardButton(back_btn_text, callback_data=back_btn_data)])
        callback_query.edit_message_text(ask_parcel_text, reply_markup=inline_keyboard)

        user_data[STATE] = EDIT_ASK_PARCEL

        return EDIT_ASK_PARCEL

    elif callback_query.data == EDIT_DATETIME:

        inline_keyboard = InlineKeyboard(dates_keyboard, user[LANG]).get_keyboard()
        inline_keyboard.inline_keyboard.append([InlineKeyboardButton(back_btn_text, callback_data=back_btn_data)])
        callback_query.edit_message_text(date_text, reply_markup=inline_keyboard)

        user_data[STATE] = EDIT_DATE

        return EDIT_DATE

    elif callback_query.data == EDIT_COMMENT:
        text = get_comment_text(user[LANG])

        inline_keyboard = callback_query.message.reply_markup
        inline_keyboard = inline_keyboard.from_column([
            InlineKeyboardButton(text[1], callback_data='no_comment'),
            InlineKeyboardButton(back_btn_text, callback_data=back_btn_data)
        ])
        callback_query.edit_message_text(text[0], reply_markup=inline_keyboard)

        user_data[STATE] = EDIT_COMMENT

        return EDIT_COMMENT

    elif callback_query.data == EDIT_COMPLETE:

        inline_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f'📝 {edit_btn_text}', callback_data='editing')],
            [InlineKeyboardButton(f'❌ {delete_btn_text}', callback_data='delete')],
        ])
        try:
            callback_query.edit_message_reply_markup(inline_keyboard)
        except TelegramError:
            pass

        return

    elif callback_query.data == EDITING:
        inline_keyboard = InlineKeyboard(edit_keyboard, user[LANG]).get_keyboard()
        try:
            callback_query.edit_message_reply_markup(inline_keyboard)
        except TelegramError:
            pass

        return

    elif callback_query.data == DELETE:

        active_driver_data = get_active_driver_by_user_id(user[ID])
        active_driver_data.pop('updated_at')
        active_driver_data['deleted_at'] = datetime.datetime.now()

        if delete_active_driver(active_driver_data[DRIVER_ID]) == 'deleted':
            callback_query.answer(alert_text, show_alert=True)
            insert_data(active_driver_data, 'active_drivers_history')

        reply_keyboard = ReplyKeyboard(driver_keyboard, user[LANG]).get_keyboard()
        callback_query.message.reply_text(alert_text, reply_markup=reply_keyboard)

        try:
            callback_query.delete_message()
        except TelegramError:
            callback_query.edit_message_reply_markup()

        user_data.clear()

        return ConversationHandler.END


def edit_region_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data

    if user[LANG] == LANGS[0]:
        from_text = "Qayerdan"
        to_text = "Qayerga"
        district_text = "(Tumanni tanlang)"
        note_text = "Izoh: Siz, bir nechta tumanlarni tanlashingiz mumkin"
        error_text = "Birorta ham tuman tanlanmadi.\n" \
                     "⚠ Iltimos, kamida bitta tumanni tanlang."

    if user[LANG] == LANGS[1]:
        from_text = "Откуда"
        to_text = "Куда"
        district_text = "(Выберите район)"
        note_text = "Примечание: Вы можете выбрать несколько районов"
        error_text = "Ни один район не был выбран.\n" \
                     "⚠ Выберите хотя бы один район."

    if user[LANG] == LANGS[2]:
        from_text = "Қаердан"
        to_text = "Қаерга"
        district_text = "(Туманни танланг)"
        note_text = "Изоҳ: Сиз, бир нечта туманларни танлашингиз мумкин"
        error_text = "Бирорта ҳам туман танланмади.\n" \
                     "⚠ Илтимос, камида битта туманни танланг."

    if user_data[STATE] == 'edit_from_region':
        state = 'edit_from_district'
        key = 'from'
        text = from_text
    elif user_data[STATE] == 'edit_to_region':
        state = 'edit_to_district'
        key = 'to'
        text = to_text

    driver_and_car_data = get_driver_and_car_data(user[ID])

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

        new_json = ujson.dumps(user_data[CHECKED][key])
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

        # logger.info('user_data: %s', user_data)
        return EDIT_DISTRICT

    active_driver_data = get_active_driver_by_user_id(user[ID])
    data_ = set_data(user, driver_and_car_data, active_driver_data)
    label = reply_keyboard_types[active_driver_keyboard][0][f'text_{user[LANG]}']
    active_driver_layout = get_active_driver_layout(user[LANG], data_, label)

    inline_keyboard = InlineKeyboard(edit_keyboard, user[LANG]).get_keyboard()
    callback_query.edit_message_text(active_driver_layout, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)
    callback_query.answer()

    user_data[STATE] = CHOOSE_EDITING
    if CHECKED in user_data:
        user_data.pop(CHECKED)

    # logger.info('user_data: %s', user_data)
    return CHOOSE_EDITING


def edit_district_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data

    if user[LANG] == LANGS[0]:
        from_text = "Qayerdan"
        to_text = "Qayerga"
        region_text = "(Viloyatni tanlang)"
        all_alert_text = "Barcha tumanlar tanlandi"
        checked_alert_text = "tanlandi"
        unchecked_alert_text = "olib tashlandi"

    if user[LANG] == LANGS[1]:
        from_text = "Откуда"
        to_text = "Куда"
        region_text = "(Выберите область)"
        all_alert_text = "Выбраны все районы"
        checked_alert_text = "выбрано"
        unchecked_alert_text = "удалено"

    if user[LANG] == LANGS[2]:
        from_text = "Қаердан"
        to_text = "Қаерга"
        region_text = "(Вилоятни танланг)"
        all_alert_text = "Барча туманлар танланди"
        checked_alert_text = "танланди"
        unchecked_alert_text = "олиб ташланди"

    if user_data[STATE] == 'edit_from_district':
        state = 'edit_from_region'
        key = 'from'
        text = from_text
    elif user_data[STATE] == 'edit_to_district':
        state = 'edit_to_region'
        key = 'to'
        text = to_text

    region_id = user_data[state]

    if data == 'back':

        back_btn_icon = inline_keyboard_types[back_next_keyboard][0]['icon']
        back_btn_text = inline_keyboard_types[back_next_keyboard][0][f'text_{user[LANG]}']
        back_btn_text = f'{back_btn_icon} {back_btn_text}'
        back_btn_data = inline_keyboard_types[back_next_keyboard][0]['data']

        inline_keyboard = InlineKeyboard(regions_keyboard, user[LANG], data=True).get_keyboard()
        inline_keyboard.inline_keyboard.append([InlineKeyboardButton(back_btn_text, callback_data=back_btn_data)])

        text = f'{text} {region_text}:'
        callback_query.edit_message_text(text, reply_markup=inline_keyboard)
        callback_query.answer()

        user_data[STATE] = state
        user_data.pop(state)

        # logger.info('user_data: %s', user_data)
        return EDIT_REGION

    elif data == 'check_all':

        reply_markup = callback_query.message.reply_markup
        inline_keyboard = reply_markup.inline_keyboard

        icon = "✅"
        action = "checked"
        district_ids_list = loop(icon, action, inline_keyboard)

        if CHECKED not in user_data:
            user_data[CHECKED] = dict()
            user_data[CHECKED][key] = dict()

        elif key not in user_data[CHECKED]:
            user_data[CHECKED][key] = dict()

        try:
            callback_query.edit_message_reply_markup(reply_markup)
            callback_query.answer(f'{icon} {all_alert_text}')

            user_data[CHECKED][key].update({region_id: district_ids_list})

        except TelegramError:
            icon = '☑'
            action = 'unchecked'
            loop(icon, action, inline_keyboard)
            callback_query.edit_message_reply_markup(reply_markup)
            callback_query.answer()

            del user_data[CHECKED][key][region_id]

        # logger.info('user_data: %s', user_data)
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
                    dirtict_name = col.text.split(maxsplit=1)[-1]
                    col.text = f'{new_icon} {dirtict_name}'
                    col.callback_data = f'{district_id}_{new_action}'
                    stop = True
                    break
            if stop:
                break

        if CHECKED not in user_data:
            user_data[CHECKED] = dict()
            user_data[CHECKED][key] = dict()

        elif key not in user_data[CHECKED]:
            user_data[CHECKED][key] = dict()

        # When user presses district button many times TelegramErrorn will be thrown
        # Error message: Message is not modified: specified new message content and reply markup are exactly
        # the same as a current content and reply markup of the message
        try:
            callback_query.edit_message_reply_markup(reply_markup)

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
                # Remove district_id if exists in user_data[CHECKED][key][region_id] list
                if district_id in user_data[CHECKED][key][region_id]:
                    user_data[CHECKED][key][region_id].remove(district_id)

                # If list is empty delete the `region_id: [districts_id]` pair
                if not user_data[CHECKED][key][region_id]:
                    del user_data[CHECKED][key][region_id]

                alert = unchecked_alert_text

            alert = f'{dirtict_name} {alert}'
            callback_query.answer(alert)

        except TelegramError:
            pass

        # logger.info('user_data: %s', user_data)
        return


def edit_empty_seats_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query

    driver_and_car_data = get_driver_and_car_data(user[ID])

    if callback_query.data != 'back':
        update_active_driver_empty_seats(int(callback_query.data), driver_and_car_data[ID])
        callback_query.answer(get_edited_alert(user[LANG]), show_alert=True)

    active_driver_data = get_active_driver_by_user_id(user[ID])
    data = set_data(user, driver_and_car_data, active_driver_data)
    label = reply_keyboard_types[active_driver_keyboard][0][f'text_{user[LANG]}']
    active_driver_layout = get_active_driver_layout(user[LANG], data, label)

    inline_keyboard = InlineKeyboard(edit_keyboard, user[LANG]).get_keyboard()
    callback_query.edit_message_text(active_driver_layout, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)
    callback_query.answer()

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

    active_driver_data = get_active_driver_by_user_id(user[ID])
    data = set_data(user, driver_and_car_data, active_driver_data)
    label = reply_keyboard_types[active_driver_keyboard][0][f'text_{user[LANG]}']
    active_driver_layout = get_active_driver_layout(user[LANG], data, label)

    inline_keyboard = InlineKeyboard(edit_keyboard, user[LANG]).get_keyboard()
    callback_query.edit_message_text(active_driver_layout, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)
    callback_query.answer()

    user_data[STATE] = CHOOSE_EDITING

    return CHOOSE_EDITING


def edit_date_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query

    if user[LANG] == LANGS[0]:
        text = "Soatni belgilang"
    if user[LANG] == LANGS[1]:
        text = "Выберите время"
    if user[LANG] == LANGS[2]:
        text = "Соатни белгиланг"

    text = f'{text}:'
    driver_and_car_data = get_driver_and_car_data(user[ID])

    if callback_query.data == 'now':
        new_departure = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        update_active_driver_departure_time(new_departure, driver_and_car_data[ID])
        callback_query.answer(get_edited_alert(user[LANG]), show_alert=True)

    elif callback_query.data != 'back':

        user_data['new_date'] = callback_query.data

        inline_keyboard = InlineKeyboard(times_keyboard, user[LANG],
                                         data={'begin': 6, 'end': 17, 'undefined': True}).get_keyboard()
        callback_query.edit_message_text(text, reply_markup=inline_keyboard)

        user_data[STATE] = EDIT_TIME

        return EDIT_TIME

    active_driver_data = get_active_driver_by_user_id(user[ID])
    data = set_data(user, driver_and_car_data, active_driver_data)
    label = reply_keyboard_types[active_driver_keyboard][0][f'text_{user[LANG]}']
    active_driver_layout = get_active_driver_layout(user[LANG], data, label)

    inline_keyboard = InlineKeyboard(edit_keyboard, user[LANG]).get_keyboard()
    callback_query.edit_message_text(active_driver_layout, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)
    callback_query.answer()

    user_data[STATE] = CHOOSE_EDITING

    return CHOOSE_EDITING


def edit_time_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
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

        driver_and_car_data = get_driver_and_car_data(user[ID])
        new_departure = f'{user_data["new_date"]} {data}'
        update_active_driver_departure_time(new_departure, driver_and_car_data[ID])

        callback_query.answer(get_edited_alert(user[LANG]), show_alert=True)
        if 'new_date' in user_data:
            user_data.pop('new_date')

        active_driver_data = get_active_driver_by_user_id(user[ID])
        data = set_data(user, driver_and_car_data, active_driver_data)
        label = reply_keyboard_types[active_driver_keyboard][0][f'text_{user[LANG]}']
        active_driver_layout = get_active_driver_layout(user[LANG], data, label)

        inline_keyboard = InlineKeyboard(edit_keyboard, user[LANG]).get_keyboard()
        callback_query.edit_message_text(active_driver_layout, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)

        user_data[STATE] = CHOOSE_EDITING

        return CHOOSE_EDITING


def edit_comment_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query

    driver_and_car_data = get_driver_and_car_data(user[ID])

    if callback_query is None:
        update_active_driver_comment(update.message.text, driver_and_car_data[ID])
        context.bot.edit_message_reply_markup(user[TG_ID], user_data[MESSAGE_ID])

    elif callback_query.data == 'no_comment':
        update_active_driver_comment(None, driver_and_car_data[ID])
        callback_query.answer(get_edited_alert(user[LANG]), show_alert=True)

    active_driver_data = get_active_driver_by_user_id(user[ID])
    data = set_data(user, driver_and_car_data, active_driver_data)
    label = reply_keyboard_types[active_driver_keyboard][0][f'text_{user[LANG]}']
    active_driver_layout = get_active_driver_layout(user[LANG], data, label)

    inline_keyboard = InlineKeyboard(edit_keyboard, user[LANG]).get_keyboard()

    if callback_query is None:
        message = update.message.reply_html(active_driver_layout, reply_markup=inline_keyboard)
        user_data[MESSAGE_ID] = message.message_id

    elif callback_query.data == 'no_comment' or callback_query.data == 'back':
        callback_query.edit_message_text(active_driver_layout, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)
        callback_query.answer()

    user_data[STATE] = CHOOSE_EDITING

    return CHOOSE_EDITING


def edit_fallback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    back_obj = re.search("(Ortga|Назад|Ортга)$", update.message.text)

    if update.message.text == '/start' or update.message.text == '/menu' or \
            update.message.text == '/cancel' or back_obj:

        if user[LANG] == LANGS[0]:
            canceled_text = "Tahrirlash bekor qilindi"
        if user[LANG] == LANGS[1]:
            canceled_text = "Редактирование отменено"
        if user[LANG] == LANGS[2]:
            canceled_text = "Таҳрирлаш бекор қилинди"

        text = f'‼ {canceled_text} !'
        keyboard = main_menu_keyboard

        if update.message.text == '/cancel' or back_obj:
            keyboard = active_driver_keyboard

        delete_message_by_message_id(context, user)

        reply_keyboard = ReplyKeyboard(keyboard, user[LANG]).get_keyboard()
        update.message.reply_text(text, reply_markup=reply_keyboard)

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

        text = f'‼ {text}.'
        update.message.reply_text(text)

        return


edit_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(r"(Aktiv holat|Активный статус|Актив ҳолат)$") &
                                 (~Filters.update.edited_message), edit_conversation_callback)],

    states={
        CHOOSE_EDITING: [CallbackQueryHandler(choose_editing_callback, pattern=r'^(edit_\w+|editing|delete)$')],

        EDIT_REGION: [CallbackQueryHandler(edit_region_callback, pattern=r'^(\d+|save_checked|back)$')],

        EDIT_DISTRICT: [
            CallbackQueryHandler(edit_district_callback, pattern=r'^(check_all|back|\d+_(checked|unchecked))$')],

        EDIT_EMPTY_SEATS: [CallbackQueryHandler(edit_empty_seats_callback, pattern=r'^(\d+|back)$')],

        EDIT_ASK_PARCEL: [CallbackQueryHandler(edit_ask_parcel_callback, pattern=r'^(yes|no|back)$')],

        EDIT_DATE: [CallbackQueryHandler(edit_date_callback, pattern=r'^(now|\d+[-]\d+[-]\d+|back)$')],

        EDIT_TIME: [CallbackQueryHandler(edit_time_callback, pattern=r'^(back|next|\d+[:]00|undefined)$')],

        EDIT_COMMENT: [CallbackQueryHandler(edit_comment_callback, pattern=r'^(no_comment|back)$'),
                       MessageHandler(Filters.regex("^(.(?!(Ortga|Назад|Ортга)))*$") & (~Filters.command) &
                                      (~Filters.update.edited_message), edit_comment_callback)],
    },
    fallbacks=[MessageHandler(Filters.text & (~Filters.update.edited_message), edit_fallback)],

    persistent=True,

    name='edit_conversation'
)
