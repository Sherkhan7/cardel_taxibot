import logging
import datetime
import ujson

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
from DB import *
from languages import LANGS
from layouts import *
from globalvariables import *
from helpers import *

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *

logger = logging.getLogger()


def activate_conversation_callback(update: Update, context: CallbackContext):
    # with open('jsons/update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    if user[LANG] == LANGS[0]:
        from_text = "Qayerdan (Viloyatni tanlang)"
        active_status_text = "Siz aktiv holatdasiz"
        activae_error_text = "Kechirasiz, aktivlashtirish uchun avval haydovchi sifatida ro'yxatdan o'ting"

    if user[LANG] == LANGS[1]:
        from_text = "Откуда (Выберите область)"
        active_status_text = "Вы активны"
        activae_error_text = "Извините, пожалуйста, сначала зарегистрируйтесь как водитель, чтобы активировать"

    if user[LANG] == LANGS[2]:
        from_text = "Қаердан (Вилоятни танланг)"
        active_status_text = "Сиз актив ҳолатдасиз"
        activae_error_text = "Кечирасиз, активлаштириш учун аввал ҳайдовчи сифатида рўйхатдан ўтинг"

    active_status_text = f'‼ {active_status_text} !'
    from_text = f'{from_text}:'
    activae_error_text = f'🛑 {activae_error_text} !'

    active_driver_data = get_active_driver_by_user_id(user[ID])
    driver_data = get_driver_by_user_id(user[ID])

    if not active_driver_data and driver_data:

        update.message.reply_text(update.message.text, reply_markup=ReplyKeyboardRemove())

        inline_keyboard = InlineKeyboard(regions_keyboard, user[LANG], data=True).get_keyboard()
        message = update.message.reply_text(from_text, reply_markup=inline_keyboard)

        user_data[MESSAGE_ID] = message.message_id
        user_data[STATE] = FROM_REGION

        return REGION

    elif driver_data is None:
        reply_keyboard = ReplyKeyboard(main_menu_keyboard, user[LANG]).get_keyboard()
        update.message.reply_text(activae_error_text, reply_markup=reply_keyboard)

        return ConversationHandler.END

    else:
        reply_keyboard = ReplyKeyboard(active_driver_keyboard, user[LANG]).get_keyboard()
        update.message.reply_text(active_status_text, reply_markup=reply_keyboard)

        user_data.clear()

        return ConversationHandler.END


def region_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data

    if user[LANG] == LANGS[0]:
        from_text = "Qayerdan"
        to_text = "Qayerga"
        district_text = "(Tumanni tanlang)"
        region_text = "(Viloyatni tanlang)"
        note_text = "Izoh: Siz, bir nechta tumanlarni tanlashingiz mumkin"
        error_text = "Birorta ham tuman tanlanmadi.\n" \
                     "⚠ Iltimos, kamida bitta tumanni tanlang."
        empty_seats_text = "Bo'sh joylar sonini tanlang"
        alert_text = "Tanlangan tumanlar saqlandi"

    if user[LANG] == LANGS[1]:
        from_text = "Откуда"
        to_text = "Куда"
        district_text = "(Выберите район)"
        region_text = "(Выберите область)"
        note_text = "Примечание: Вы можете выбрать несколько районов"
        error_text = "Ни один район не был выбран.\n" \
                     "⚠ Выберите хотя бы один район."
        empty_seats_text = "Выберите количество свободных мест"
        alert_text = "Выбранные районы сохранены"

    if user[LANG] == LANGS[2]:
        from_text = "Қаердан"
        to_text = "Қаерга"
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
        text = from_text
    elif user_data[STATE] == TO_REGION:
        state = TO_DISTRICT
        key = 'to'
        text = to_text

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

        if user_data[STATE] == FROM_REGION:
            state = TO_REGION
            return_state = REGION
            text = f'{to_text} {region_text}:'
            alert_text = f'✅ {alert_text}\n\n{text}'
            callback_query.answer(alert_text, show_alert=True)
            reply_markup = callback_query.message.reply_markup
            callback_query.edit_message_text(text, reply_markup=reply_markup)

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

        # logger.info('user_data: %s', user_data)
        return return_state

    else:

        region_id = user_data[user_data[STATE]] = data = int(data)

        if CHECKED in user_data and key in user_data[CHECKED] and region_id in user_data[CHECKED][key]:
            data = {region_id: user_data[CHECKED][key][region_id]}

        text = f'{text} {district_text}:\n\n' \
               f'🔅 {wrap_tags(note_text)}'
        inline_keyboard = InlineKeyboard(districts_selective_keyboard, user[LANG], data=data).get_keyboard()

        callback_query.edit_message_text(text, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)
        callback_query.answer()

        user_data[STATE] = state

        # logger.info('user_data: %s', user_data)
        return DISTRICT


def district_callback(update: Update, context: CallbackContext):
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

    if user_data[STATE] == FROM_DISTRICT:
        state = FROM_REGION
        key = 'from'
        text = from_text
    elif user_data[STATE] == TO_DISTRICT:
        state = TO_REGION
        key = 'to'
        text = to_text

    region_id = user_data[state]

    if data == 'back':

        text = f'{text} {region_text}:'
        inline_keyboard = InlineKeyboard(regions_keyboard, user[LANG], data=True).get_keyboard()

        callback_query.edit_message_text(text, reply_markup=inline_keyboard)
        callback_query.answer()

        user_data[STATE] = state
        user_data.pop(state)

        # logger.info('user_data: %s', user_data)
        return REGION

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

    # logger.info('user_data: %s', user_data)
    return ASK_PARCEL


def ask_parcel_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    user_data[ASK_PARCEL] = True if callback_query.data == 'yes' else False

    if user[LANG] == LANGS[0]:
        text = "Ketish kunini belgilang"

    if user[LANG] == LANGS[1]:
        text = "Установите дату отъезда"

    if user[LANG] == LANGS[2]:
        text = "Кетиш кунини белгиланг"

    text = f'{text}:'
    inline_keyboard = InlineKeyboard(dates_keyboard, user[LANG]).get_keyboard()
    callback_query.edit_message_text(text, reply_markup=inline_keyboard)

    user_data[STATE] = DATE

    # logger.info('user_data: %s', user_data)
    return DATE


def date_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data
    callback_query.answer()

    if data == 'now':

        user_data[DATE] = datetime.datetime.now().strftime('%d-%m-%Y')
        user_data[TIME] = 'now'

        text = get_comment_text(user[LANG])
        inline_keyboard = callback_query.message.reply_markup
        inline_keyboard = inline_keyboard.from_button(InlineKeyboardButton(text[1], callback_data='no_comment'))
        callback_query.edit_message_text(text[0], reply_markup=inline_keyboard)

        user_data[STATE] = COMMENT

        # logger.info('user_data: %s', user_data)
        return COMMENT

    else:

        user_data[DATE] = data

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

        user_data[STATE] = TIME

        # logger.info('user_data: %s', user_data)
        return TIME


def time_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data
    callback_query.answer()

    if data == 'next' or data == 'back':

        if data == 'next':
            inline_keyboard = InlineKeyboard(times_keyboard, user[LANG],
                                             data={'begin': 18, 'end': 29, 'undefined': True}).get_keyboard()
        if data == 'back':
            inline_keyboard = InlineKeyboard(times_keyboard, user[LANG],
                                             data={'begin': 6, 'end': 17, 'undefined': True}).get_keyboard()

        callback_query.edit_message_reply_markup(inline_keyboard)

        # logger.info('user_data: %s', user_data)
        return

    else:

        user_data[TIME] = data

        text = get_comment_text(user[LANG])
        inline_keyboard = callback_query.message.reply_markup
        inline_keyboard = inline_keyboard.from_button(InlineKeyboardButton(text[1], callback_data='no_comment'))
        callback_query.edit_message_text(text[0], reply_markup=inline_keyboard)

        user_data[STATE] = COMMENT
        # logger.info('user_data: %s', user_data)
        return COMMENT


def comment_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query

    inline_keyboard = InlineKeyboard(confirm_keyboard, user[LANG]).get_keyboard()
    driver_and_car_data = get_driver_and_car_data(user[ID])

    user_data[FULLNAME] = user[FULLNAME]
    user_data[PHONE_NUMBER] = user[PHONE_NUMBER]
    user_data[PHONE_NUMBER_2] = user[PHONE_NUMBER_2]
    user_data[DRIVER_ID] = driver_and_car_data[ID]
    user_data[CAR_MODEL] = driver_and_car_data[CAR_MODEL]
    user_data[BAGGAGE] = driver_and_car_data[BAGGAGE]

    if callback_query is None:

        user_data[COMMENT] = update.message.text
        context.bot.edit_message_reply_markup(user[TG_ID], user_data[MESSAGE_ID])

        layout = get_active_driver_layout(user[LANG], data=user_data)
        message = update.message.reply_html(layout, reply_markup=inline_keyboard)
        user_data[MESSAGE_ID] = message.message_id

    else:

        user_data[COMMENT] = None
        layout = get_active_driver_layout(user[LANG], data=user_data)
        callback_query.edit_message_text(layout, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)

    user_data[STATE] = CONFIRMATION
    # logger.info('user_data: %s', user_data)
    return CONFIRMATION


def confirmation_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data

    if user[LANG] == LANGS[0]:
        canceled_text = "Aktivlashtirish bekor qilindi"
        confirmed_text = "Aktivlashtirish tasdiqlandi"
        canceled_status = "Bekor qilindi"
        confirmed_status = "Taqsdiqlangan"

    if user[LANG] == LANGS[1]:
        canceled_text = "Активация отменена"
        confirmed_text = "Активация подтверждена"
        canceled_status = "Отменено"
        confirmed_status = "Одобрено"

    if user[LANG] == LANGS[2]:
        canceled_text = "Активлаштириш бекор қилинди"
        confirmed_text = "Активлаштириш тасдиқланди"
        canceled_status = "Бекор қилинди"
        confirmed_status = "Тасдиқланган"

    if data == 'cancel':
        icon = '🔴'
        text = f'‼ {canceled_text} !'
        status = canceled_status
        keyboard = driver_keyboard

    elif data == 'confirm':
        icon = '🟢'
        text = f'✅ {confirmed_text}'
        keyboard = active_driver_keyboard
        status = confirmed_status

        data = dict()
        data[DRIVER_ID] = user_data[DRIVER_ID]
        data[USER_ID] = user[ID]
        data['from_'] = ujson.dumps(user_data[CHECKED]['from'])
        data['to_'] = ujson.dumps(user_data[CHECKED]['to'])
        data[EMPTY_SEATS] = user_data[EMPTY_SEATS]
        data[ASK_PARCEL] = user_data[ASK_PARCEL]
        data[COMMENT] = user_data[COMMENT]

        if user_data[TIME] == 'now':
            data[DEPARTURE_TIME] = datetime.datetime.now()
            data[DEPARTURE_TIME] = data[DEPARTURE_TIME].strftime("%d-%m-%Y %H:%M")
        else:
            data[DEPARTURE_TIME] = f'{user_data[DATE]} {user_data[TIME]}'

        table = 'active_drivers'
        # logger.info('user_data: %s', user_data)
        insert_data(data, table)

    message_text = callback_query.message.text_html
    message_text += f'\n\n{icon} Status: {status}'
    callback_query.edit_message_text(message_text, parse_mode=ParseMode.HTML)

    reply_keyboard = ReplyKeyboard(keyboard, user[LANG]).get_keyboard()
    callback_query.message.reply_text(text, reply_markup=reply_keyboard)

    user_data.clear()

    return ConversationHandler.END


def activate_fallback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    if update.message.text == '/start' or update.message.text == '/menu' or update.message.text == '/cancel':

        if user[LANG] == LANGS[0]:
            text = "Aktivlashtirish bekor qilindi"
        if user[LANG] == LANGS[1]:
            text = "Активация отменена"
        if user[LANG] == LANGS[2]:
            text = "Активлаштириш бекор қилинди"

        text = f'‼ {text} !'
        keyboard = driver_keyboard if update.message.text == '/cancel' else main_menu_keyboard
        delete_message_by_message_id(context, user)

        reply_keyboard = ReplyKeyboard(keyboard, user[LANG]).get_keyboard()
        update.message.reply_text(text, reply_markup=reply_keyboard)

        user_data.clear()
        return ConversationHandler.END

    else:

        if user[LANG] == LANGS[0]:
            text = "Hozir siz aktivlashtirish bo'limidasiz.\n\n" \
                   "Aktivlashtirishni to'xtatish uchun /cancel ni bosing.\n\n" \
                   "Bosh menyuga qaytish uchun /menu ni bosing"

        if user[LANG] == LANGS[1]:
            text = "Вы сейчас в разделе активации.\n\n" \
                   "Нажмите /cancel, чтобы остановить активацию.\n\n" \
                   "Нажмите /menu, чтобы вернуться в главное меню"

        if user[LANG] == LANGS[2]:
            text = "Ҳозир сиз активлаштириш бўлимидасиз.\n\n" \
                   "Активлаштиришни тўхтатиш учун /cancel ни босинг.\n\n" \
                   "Бош менюга қайтиш учун /menu ни босинг"

        text = f'‼ {text}.'
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

        DATE: [CallbackQueryHandler(date_callback, pattern=r'^(now|\d+[-]\d+[-]\d+)$')],

        TIME: [CallbackQueryHandler(time_callback, pattern=r'^(back|next|\d+[:]00|undefined)$')],

        COMMENT: [CallbackQueryHandler(comment_callback, pattern=r'^no_comment$'),
                  MessageHandler(Filters.text & (~Filters.command) & (~Filters.update.edited_message),
                                 comment_callback)],

        CONFIRMATION: [CallbackQueryHandler(confirmation_callback, pattern='^(confirm|cancel)$')]
    },
    fallbacks=[MessageHandler(Filters.text & (~Filters.update.edited_message), activate_fallback)],

    persistent=True,

    name='activate_conversation'
)
