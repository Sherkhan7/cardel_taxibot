import datetime
import pytz

from telegram.ext import Updater, PicklePersistence

from config import TOKEN, SERVER_IP, PORT, URL
from errorhandler import error_handler
from helpers import run_note_callback
from handlers import *


def main():
    my_persistence = PicklePersistence(filename='my_pickle', single_file=False, store_chat_data=False)

    updater = Updater(TOKEN, persistence=my_persistence)

    updater.dispatcher.add_handler(sendpost_conversation_handler)

    updater.dispatcher.add_handler(command_handler)

    updater.dispatcher.add_handler(edit_user_data_conversation_handler)

    updater.dispatcher.add_handler(edit_driver_data_conversation_handler)

    updater.dispatcher.add_handler(edit_conversation_handler)

    updater.dispatcher.add_handler(activate_conversation_handler)

    updater.dispatcher.add_handler(driver_conversation_handler)

    updater.dispatcher.add_handler(search_conversation_handler)
    # updater.dispatcher.add_handler(announce_conversation_handler)

    updater.dispatcher.add_handler(registration_conversation_handler)

    updater.dispatcher.add_handler(message_handler)

    updater.dispatcher.add_handler(callback_query_handler)

    updater.job_queue.run_daily(run_note_callback, datetime.time(hour=5, tzinfo=pytz.timezone('Asia/Tashkent')),
                                name='daily_note_active_drivers')

    # adding error handler
    updater.dispatcher.add_error_handler(error_handler)

    # updater.start_polling()
    updater.start_webhook(port=PORT, url_path=TOKEN, webhook_url=URL + TOKEN, ip_address=SERVER_IP)

    updater.idle()


if __name__ == '__main__':
    main()
