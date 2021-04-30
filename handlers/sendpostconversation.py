import logging
import re
import ujson
import datetime
import time

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InputFile,
    TelegramError,
    ParseMode,
)
from telegram.ext import (
    CallbackQueryHandler,
    MessageHandler,
    CommandHandler,
    ConversationHandler,
    CallbackContext,
    Filters
)
from DB import *
from globalvariables import *
from config import DEVELOPER_CHAT_ID, BOT_USERNAME
from languages import LANGS
from helpers import delete_message_by_message_id

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import main_menu_keyboard

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import yes_no_keyboard

logger = logging.getLogger()


def send_messages(context: CallbackContext):
    user = context.job.context[0]
    user_data = context.job.context[-1]

    errors_list = []
    all_users = get_all_users()

    if 'post_photo' in user_data:

        photo = user_data['post_photo'][-1].file_id
        caption = user_data['caption']

        start_time = datetime.datetime.now()
        for u in all_users:
            try:
                time.sleep(0.3)
                context.bot.send_photo(u[TG_ID], photo, caption=caption, parse_mode=ParseMode.HTML)
            except TelegramError as e:
                errors_list.append({'user_id': u[ID], 'user_tg_id': u[TG_ID], 'error_message': e.message})
        end_time = datetime.datetime.now()

    if 'post_video' in user_data:
        video = user_data['post_video'].file_id
        caption = user_data['caption']

        start_time = datetime.datetime.now()
        for u in all_users:
            try:
                time.sleep(0.3)
                context.bot.send_video(u[TG_ID], video, caption=caption, parse_mode=ParseMode.HTML)
            except TelegramError as e:
                errors_list.append({'user_id': u[ID], 'user_tg_id': u[TG_ID], 'error_message': e.message})
        end_time = datetime.datetime.now()

    if 'post_text' in user_data:

        start_time = datetime.datetime.now()
        for u in all_users:
            try:
                time.sleep(0.5)
                context.bot.send_message(u[TG_ID], text=user_data['post_text'])
            except TelegramError as e:
                errors_list.append({'user_id': u[ID], 'user_tg_id': u[TG_ID], 'error_message': e.message})
        end_time = datetime.datetime.now()

    text = f'✅ Sending this message to all users have been successfully finished!'
    context.bot.send_message(chat_id=user[TG_ID], text=text, reply_to_message_id=user_data[MESSAGE_ID])

    errors_list.insert(0, {
        'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S.%f'),
        'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S.%f'),
        'delta': f'{(end_time - start_time).total_seconds()}s',
        'users_count': len(all_users),
        'errors_count': len(errors_list)
    })

    path = f'/var/www/html/{BOT_USERNAME}/logs/'
    document_name = datetime.datetime.now().strftime("sent_post_%d-%m-%Y_%H-%M-%S") + '.txt'
    full_path = path + document_name

    with open(full_path, 'w') as f:
        f.write(ujson.dumps(errors_list, indent=3))
    with open(full_path, 'r') as f:
        document = InputFile(f)
    context.bot.send_document(DEVELOPER_CHAT_ID, document=document)

    # Update post status
    update_post_status('sent', user_data['post_id'])


def sendpost_conversation_callback(update: Update, context: CallbackContext):
    # with open('jsons/update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    if user[TG_ID] == DEVELOPER_CHAT_ID:
        if user[LANG] == LANGS[0]:
            text = "Ajoyib, endi menga rasm, video yoki xabar yuboring"
        if user[LANG] == LANGS[1]:
            text = "Отлично, пришлите мне изображение, видео или сообщение прямо сейчас"
        if user[LANG] == LANGS[2]:
            text = "Ажойиб, энди менга расм, видео ёки хабар юборинг"

        text = f'🙂 {text}'
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

        user_data[STATE] = POST_CONTENT

        return POST_CONTENT

    else:
        if user[LANG] == LANGS[0]:
            text = "Kechirasiz, siz foydalanuvchilarga xabar yubora olmaysiz"
        if user[LANG] == LANGS[1]:
            text = "Извините, вы не можете отправлять сообщения пользователям"
        if user[LANG] == LANGS[2]:
            text = "Кечирасиз, сиз фойдаланувчиларга хабар юбора олмайсиз"

        text = f'❗ {text} 😬'
        update.message.reply_text(text)

        return ConversationHandler.END


def post_content_callback(update: Update, context: CallbackContext):
    # with open('jsons/update.json', 'a') as update_file:
    #     update_file.write(ujson.dumps(update.to_dict(), indent=3, ensure_ascii=False))
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    caption = update.message.caption_html

    # List of PhotoSize objects
    photo = update.message.photo
    video = update.message.video

    if user[LANG] == LANGS[0]:
        error_text = "Kechirasiz, yuborilgan rasmda yoki videoda izoh yo'q.\n\n" \
                     "Rasm yoki videoni izoh bilan yuboring"
        ask_text = "Xabarni tasdiqlaysizmi"
        main_menu_text = "Bosh menyu"
        perfect_text = "Ajoyib"

    if user[LANG] == LANGS[1]:
        error_text = "К сожалению, нет ни одного комментария на фото или видео, отправленного.\n\n" \
                     "Отправить картинку или видео с комментарием"
        ask_text = "Вы подтверждаете сообщение"
        main_menu_text = "Главное меню"
        perfect_text = "Отлично"

    if user[LANG] == LANGS[2]:
        error_text = "Кечирасиз, юборилган расмда ёки видеода изоҳ йўқ.\n\n" \
                     "Расм ёки видеони изоҳ билан юборинг"
        ask_text = "Хабарни тасдиқлайсизми"
        main_menu_text = "Бош меню"
        perfect_text = "Ажойиб"

    ask_text += ' ?'
    error_text = f'‼ {error_text} !'
    perfect_text = f'✅ {perfect_text} !'

    if (video or photo) and caption is None:
        update.message.reply_text(error_text, quote=True)
        return user_data[STATE]

    inline_keyboard = InlineKeyboard(yes_no_keyboard, user[LANG]).get_keyboard()
    inline_keyboard.inline_keyboard.insert(0, [InlineKeyboardButton(ask_text, callback_data='none')])

    reply_keyboard = ReplyKeyboardMarkup([
        [KeyboardButton(f'🏠 {main_menu_text}')]
    ], resize_keyboard=True)
    update.message.reply_text(perfect_text, reply_markup=reply_keyboard)

    if photo:
        user_data['post_photo'] = photo
        message = update.message.reply_photo(photo[-1].file_id, caption=caption, reply_markup=inline_keyboard,
                                             parse_mode=ParseMode.HTML)
    elif video:
        user_data['post_video'] = video
        message = update.message.reply_video(video.file_id, caption=caption, reply_markup=inline_keyboard,
                                             parse_mode=ParseMode.HTML)
    else:
        user_data['post_text'] = update.message.caption_html
        message = update.message.reply_text(user_data['post_text'], reply_markup=inline_keyboard,
                                            parse_mode=ParseMode.HTML)
    user_data['caption'] = caption
    user_data[STATE] = SEND_POST_CONFIRMATION
    user_data[MESSAGE_ID] = message.message_id

    # logger.info('user_data: %s', user_data)
    return SEND_POST_CONFIRMATION


def confirmation_send_post_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data

    if user[LANG] == LANGS[0]:
        confirmed_text = "Barcha foydalanuvchilarga xabar yuborish boshlandi. Biroz kuting"
        not_confirmed_text = "Xabar tasqdiqlanmadi"
    if user[LANG] == LANGS[1]:
        confirmed_text = "Отправка сообщений всем пользователям началась. Подождите минуту"
        not_confirmed_text = "Сообщение не было подтверждено"
    if user[LANG] == LANGS[2]:
        confirmed_text = "Барча фойдаланувчиларга хабар юбориш бошланди. Бироз кутинг"
        not_confirmed_text = "Хабар тасқдиқланмади"

    not_confirmed_text = f"❌ {not_confirmed_text} !"
    confirmed_text = f"✅ {confirmed_text} !"

    if data != 'none':

        if data == 'no':
            try:
                callback_query.delete_message()
            except TelegramError:
                callback_query.edit_message_reply_markup()
            reply_text = not_confirmed_text

        else:

            reply_text = confirmed_text

            post_data = dict()
            post_data['caption'] = user_data['caption'] if 'caption' in user_data else user_data['post_text']
            post_data[STATUS] = 'sending'
            post_data['sent_by'] = user[ID]

            # Write post to database
            post_id = insert_data(post_data, 'posts')
            user_data['post_id'] = post_id

            if 'post_photo' in user_data:

                post_photo_sizes = []
                for photo in user_data['post_photo']:
                    photo = photo.to_dict()
                    post_photo_sizes.append((
                        post_id, photo['file_id'], photo['file_unique_id'],
                        photo['width'], photo['height'], photo['file_size']
                    ))

                fields_list = ["post_id", "file_id", "file_unique_id", "width", "height", "file_size"]
                insert_order_items(post_photo_sizes, fields_list, 'post_document_sizes')

            elif 'post_video' in user_data:
                post_photo_sizes = [(
                    post_id,
                    user_data['post_video'].file_id,
                    user_data['post_video'].file_unique_id,
                    user_data['post_video'].width,
                    user_data['post_video'].height,
                    user_data['post_video'].duration,
                    user_data['post_video'].mime_type,
                    user_data['post_video'].file_size,
                )]

                fields_list = [
                    "post_id", "file_id", "file_unique_id", "width", "height", "duration", "mime_type", "file_size"
                ]
                insert_order_items(post_photo_sizes, fields_list, 'post_document_sizes')

            job_q = context.job_queue
            job_q.run_once(send_messages, 1, name='my_job', context=[user, dict(user_data)])

            callback_query.edit_message_reply_markup()

        callback_query.answer(reply_text, show_alert=True)

        reply_keyboard = ReplyKeyboard(main_menu_keyboard, user[LANG]).get_keyboard()
        callback_query.message.reply_text(reply_text, reply_markup=reply_keyboard)

        user_data.clear()
        return ConversationHandler.END

    callback_query.answer()


def sendpost_conversation_fallback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    main_menu_obj = re.search("(Bosh menyu|Главное меню|Бош меню)$", update.message.text)

    if update.message.text == '/start' or update.message.text == '/cancel' \
            or update.message.text == '/menu' or main_menu_obj:

        if user[LANG] == LANGS[0]:
            text = "Bosh menyu"
        if user[LANG] == LANGS[1]:
            text = "Главное меню"
        if user[LANG] == LANGS[2]:
            text = "Бош меню"

        text = f'🏠 {text}'
        keyboard = ReplyKeyboard(main_menu_keyboard, user[LANG]).get_keyboard()

        delete_message_by_message_id(context, user)

        update.message.reply_text(text, reply_markup=keyboard)
        user_data.clear()

        # logger.info('user_data: %s', user_data)
        return ConversationHandler.END


sendpost_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('sendpost', sendpost_conversation_callback, filters=~Filters.update.edited_message)],

    states={
        POST_CONTENT: [
            MessageHandler(
                (Filters.photo | Filters.video | Filters.text) & (~Filters.update.edited_message) & (~Filters.command),
                post_content_callback)],

        SEND_POST_CONFIRMATION: [CallbackQueryHandler(confirmation_send_post_callback, pattern=r'(yes|no)|none')]

    },
    fallbacks=[MessageHandler(Filters.text & (~Filters.update.edited_message), sendpost_conversation_fallback)],

    persistent=True,

    name='sendpost_conversation'
)
