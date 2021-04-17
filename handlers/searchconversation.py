import logging
import re
import ujson

from telegram import (
    Update,
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    KeyboardButton,
    TelegramError
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
from layouts import get_active_driver_layout
from globalvariables import *
from helpers import *

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *

logger = logging.getLogger()


def search_conversation_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    if user[LANG] == LANGS[0]:
        choose_region_text = "Qayerdan (Viloyatni tanlang)"

    if user[LANG] == LANGS[1]:
        choose_region_text = "Откуда (Выберите область)"

    if user[LANG] == LANGS[2]:
        choose_region_text = "Қаердан (Вилоятни танланг)"

    choose_region_text = f'{choose_region_text}:'
    inline_keyboard = InlineKeyboard(regions_keyboard, user[LANG]).get_keyboard()

    update.message.reply_text(update.message.text, reply_markup=ReplyKeyboardRemove())
    message = update.message.reply_text(choose_region_text, reply_markup=inline_keyboard)

    user_data[STATE] = FROM_REGION
    user_data[MESSAGE_ID] = message.message_id

    return REGION


def region_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query

    if user[LANG] == LANGS[0]:
        from_text = "Qayerdan"
        to_text = "Qayerga"
        district_text = "(Tumanni tanlang)"

    if user[LANG] == LANGS[1]:
        from_text = "Откуда"
        to_text = "Куда"
        district_text = "(Выберите район)"

    if user[LANG] == LANGS[2]:
        from_text = "Қаердан"
        to_text = "Қаерга"
        district_text = "(Туманни танланг)"

    if user_data[STATE] == FROM_REGION:
        state = FROM_DISTRICT
        text = from_text

    elif user_data[STATE] == TO_REGION:
        text = to_text
        state = TO_DISTRICT

    text = f'{text} {district_text}:'

    region_id = callback_query.data
    user_data[user_data[STATE]] = str(region_id)

    inline_keyboard = InlineKeyboard(districts_keyboard, user[LANG], data=region_id).get_keyboard()

    callback_query.edit_message_text(text, reply_markup=inline_keyboard)
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
        stop_btn = "Qidiruvni to'xtatish"
        set_seats_text = "Yo'lovchi sonini belgilang"

    if user[LANG] == LANGS[1]:
        from_text = "Откуда"
        to_text = "Куда"
        region_text = "(Выберите область)"
        stop_btn = "Остановить поиск"
        set_seats_text = "Укажите количество пассажиров"

    if user[LANG] == LANGS[2]:
        from_text = "Қаердан"
        to_text = "Қаерга"
        region_text = "(Вилоятни танланг)"
        stop_btn = "Қидирувни тўхтатиш"
        set_seats_text = "Йўловчи сонини белгиланг"

    if data == 'back' or user_data[STATE] == FROM_DISTRICT:

        if data == 'back':
            if user_data[STATE] == FROM_DISTRICT:
                state = FROM_REGION
                text = from_text
            elif user_data[STATE] == TO_DISTRICT:
                text = to_text
                state = TO_REGION

            user_data.pop(state)

        else:
            state = TO_REGION
            text = to_text
            user_data[user_data[STATE]] = int(data)

        text = f'{text} {region_text}:'
        inline_keyboard = InlineKeyboard(regions_keyboard, user[LANG]).get_keyboard()
        callback_query.edit_message_text(text, reply_markup=inline_keyboard)
        callback_query.answer()

        user_data[STATE] = state

        # logger.info('user_data: %s', user_data)
        return REGION

    elif user_data[STATE] == TO_DISTRICT:

        user_data[user_data[STATE]] = int(data)

        reply_keyboard = ReplyKeyboardMarkup([
            [
                KeyboardButton('1'),
                KeyboardButton('2'),
                KeyboardButton('3'),
                KeyboardButton('4'),
            ],
            [KeyboardButton(f'🔍 {stop_btn}')]
        ], resize_keyboard=True)

        try:
            callback_query.delete_message()
        except TelegramError:
            callback_query.edit_message_reply_markup()

        callback_query.message.reply_text(set_seats_text, reply_markup=reply_keyboard)

        user_data[STATE] = EMPTY_SEATS
        user_data.pop(MESSAGE_ID)

        # logger.info('user_data: %s', user_data)
        return EMPTY_SEATS


def empty_seats_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    stop_search = re.search("(Qidiruvni to'xtatish|Остановить поиск|Қидирувни тўхтатиш)$", update.message.text)

    if user[LANG] == LANGS[0]:
        not_found_text = "Kechirasiz, birortaham taksi topilmadi"
        found_text = "Barcha topilgan taksilar soni"
        stop_search_text = "Qidiruv to'xtatildi"
        from_text = "Qayerdan"
        to_text = "Qayerga"
        empty_seats_text = "Yo'lovchi soni"
        search_text = "Qidiruv so'rovi"
        search_result_text = "Qidiruv natijasi"

    if user[LANG] == LANGS[1]:
        not_found_text = "К сожалению, не было найдено ни одного такси"
        found_text = "Всего найдено такси"
        stop_search_text = "Поиск был остановлен"
        from_text = "Откуда"
        to_text = "Куда"
        empty_seats_text = "Количество пассажиров"
        search_text = "Поисковый запрос"
        search_result_text = "Результаты поиска"

    if user[LANG] == LANGS[2]:
        not_found_text = "Кечирасиз, бирортаҳам такси топилмади"
        found_text = "Барча топилган таксилар сони"
        stop_search_text = "Қидирув тўхтатилди"
        from_text = "Қаердан"
        to_text = "Қаерга"
        empty_seats_text = "Йўловчи сони"
        search_text = "Қидирув сўрови"
        search_result_text = "Қидирув натижаси"

    if stop_search:
        stop_search_text = f'‼ {stop_search_text}!'
        reply_keyboard = ReplyKeyboard(main_menu_keyboard, user[LANG]).get_keyboard()
        update.message.reply_text(stop_search_text, reply_markup=reply_keyboard)

        user_data.clear()
        return ConversationHandler.END

    user_data[EMPTY_SEATS] = int(update.message.text)

    from_point = get_region_and_district(user_data[FROM_REGION], user_data[FROM_DISTRICT])
    from_region_name = from_point[0][f'name_{user[LANG]}']
    from_district_name = from_point[1][f'name_{user[LANG]}']

    to_point = get_region_and_district(user_data[TO_REGION], user_data[TO_DISTRICT])
    to_region_name = to_point[0][f'name_{user[LANG]}']
    to_district_name = to_point[1][f'name_{user[LANG]}']

    search_query_text = f"{wrap_tags(search_text)}:\n\n" \
                        f"📍 {from_text}: <b>{from_region_name}, {from_district_name}</b>\n\n" \
                        f"🏁 {to_text}: <b>{to_region_name}, {to_district_name}</b>\n\n" \
                        f"🏃 {empty_seats_text}: <b>{update.message.text}</b>"

    search_from_region_id = user_data[FROM_REGION]
    search_from_district_id = user_data[FROM_DISTRICT]

    search_to_region_id = user_data[TO_REGION]
    search_to_district_id = user_data[TO_DISTRICT]

    empty_seats_list = [i for i in range(user_data[EMPTY_SEATS], 5)]
    active_drivers = get_active_drivers_by_seats(empty_seats_list)

    found_active_drivers = []
    for active_driver in active_drivers:
        from_ = ujson.loads(active_driver['from_'])
        to_ = ujson.loads(active_driver['to_'])
        found_from_region = search_from_region_id in from_
        found_to_region = search_to_region_id in to_

        if found_from_region and found_to_region:

            found_from_district = search_from_district_id in from_[search_from_region_id]
            found_to_district = search_to_district_id in to_[search_to_region_id]

            if found_to_district and found_from_district:
                found_active_drivers.append(active_driver)

    found_active_drivers_num = len(found_active_drivers)

    if not found_active_drivers:
        text = f'{search_query_text}\n\n' \
               f'{wrap_tags(search_result_text)}:\n\n' \
               f'🙊 {not_found_text}'
        update.message.reply_html(text)

    else:

        for found_active_driver in found_active_drivers:
            driver = get_driver_by_id(found_active_driver[DRIVER_ID])
            driver_user_data = get_user(driver[USER_ID])
            driver_and_car_data = get_driver_and_car_data(driver[USER_ID])
            data = set_data(driver_user_data, driver_and_car_data, found_active_driver)

            layout = get_active_driver_layout(user[LANG], data=data)
            update.message.reply_html(layout)

        text = f'\n\n{wrap_tags(search_result_text)}:\n\n' \
               f'🚕  {found_text}: <b>{found_active_drivers_num}</b>'
        text = search_query_text + text
        update.message.reply_html(text)

    data_ = {
        USER_ID: user[ID],
        FROM_REGION: user_data[FROM_REGION],
        FROM_DISTRICT: user_data[FROM_DISTRICT],
        TO_REGION: user_data[TO_REGION],
        TO_DISTRICT: user_data[TO_DISTRICT],
        EMPTY_SEATS: user_data[EMPTY_SEATS],
        'found_active_drivers': found_active_drivers_num,
    }
    insert_data(data_, 'search_history')

    # logger.info('user_data: %s', user_data)
    return


def search_fallback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    if update.message.text == '/start' or update.message.text == '/menu' or update.message.text == '/cancel':

        if user[LANG] == LANGS[0]:
            text = "Qidruv bekor qilindi"
        if user[LANG] == LANGS[1]:
            text = "Поиск отменено"
        if user[LANG] == LANGS[2]:
            text = "Қидирув бекор қилинди"

        text = f'‼ {text} !'
        delete_message_by_message_id(context, user)

        reply_keyboard = ReplyKeyboard(main_menu_keyboard, user[LANG]).get_keyboard()
        update.message.reply_text(text, reply_markup=reply_keyboard)

        user_data.clear()

        return ConversationHandler.END

    else:

        if user[LANG] == LANGS[0]:
            text = "Hozir siz taksi qidirish bo'limidasiz.\n\n" \
                   "Qidiruvni to'xtatish uchun /cancel ni bosing"

        if user[LANG] == LANGS[1]:
            text = "Сейчас вы находитесь в разделе поиска такси.\n\n" \
                   "Нажмите /cancel, чтобы остановить поиск"

        if user[LANG] == LANGS[2]:
            text = "Ҳозир сиз такси қидириш бўлимидасиз.\n\n" \
                   "Қидирувни тўхтатиш учун /cancel ни босинг"

        text = f'‼ {text}.'
        update.message.reply_text(text)

        return


search_conversation_handler = ConversationHandler(
    entry_points=[
        MessageHandler(Filters.regex(r"(Taksi qidirish|Поиск такси|Такси қидириш)$") & (~Filters.update.edited_message),
                       search_conversation_callback)],

    states={
        REGION: [CallbackQueryHandler(region_callback, pattern=r'^\d+$')],

        DISTRICT: [CallbackQueryHandler(district_callback, pattern=r'^(back|\d+)$')],

        EMPTY_SEATS: [
            MessageHandler(Filters.regex("([1-4])|(Qidiruvni to'xtatish|Остановить поиск|Қидирувни тўхтатиш)"),
                           empty_seats_callback)],
    },

    fallbacks=[MessageHandler(Filters.text & (~Filters.update.edited_message), search_fallback)],

    persistent=True,

    name='search_conversation'
)
