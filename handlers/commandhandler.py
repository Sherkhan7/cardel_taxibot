import ujson
import pickle

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler


def do_command(update: Update, context: CallbackContext):
    # with open('jsons/update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    full_text = update.message.text.split() if update.message else update.edited_message.text.split()
    persistence = context.dispatcher.persistence

    if full_text[0] == '/getjob':
        current_jobs = context.job_queue.get_jobs_by_name('daily_note_active_drivers')
        for job in current_jobs:
            if update.message:
                update.message.reply_text(str(job.next_t))
            else:
                update.edited_message.reply_text(str(job.next_t))

        return

    if len(full_text) == 2:
        command = full_text[0]
        user_id = int(full_text[-1])

        if command == '/getuserdata':
            user_data = persistence.get_user_data()[user_id]

            if user_data:
                user_conversations = ''
                text = ujson.dumps(user_data, indent=3, ensure_ascii=False)
                conversations = pickle.load(open('my_pickle_conversations', 'rb'))

                for conv_name, conv_dict in conversations.items():
                    if (user_id, user_id) in conv_dict:
                        user_conversations += f"{conv_name}: {conv_dict[(user_id, user_id)]}\n"
                text += f'\n{user_conversations}'

            else:
                text = 'user_tg_id topilmadi !\n' \
                       f'Tip: {command} user_tg_id'

            text = f'<pre>{text}</pre>'
            if update.message:
                update.message.reply_html(text)
            else:
                update.edited_message.reply_html(text)

    elif len(full_text) == 3:
        command = full_text[0]
        user_id = int(full_text[1])
        conversation_name = full_text[-1]

        if command == '/getuserstate':
            conversation_data = persistence.get_conversations(conversation_name)

            if conversation_data and (user_id, user_id) in conversation_data:
                state = conversation_data[(user_id, user_id)]
            else:
                state = 'user_tg_id yoki conversation_name xato !\n' \
                        f'Tip: {command} user_tg_id conversation_name'

            state = f'<pre>State: {state}</pre>'
            if update.message:
                update.message.reply_html(state)
            else:
                update.edited_message.reply_html(state)

    elif len(full_text) == 4:
        command = full_text[0]
        user_id = int(full_text[1])
        conversation_name = full_text[2]
        new_state = full_text[-1]

        if command == '/updateuserstate':
            conversation_data = persistence.get_conversations(conversation_name)

            if conversation_data and (user_id, user_id) in conversation_data:
                new_state = None if new_state.lower() == 'none' else new_state
                persistence.update_conversation(conversation_name, (user_id, user_id), new_state)
                text = f"[{user_id}], [{conversation_name}] bo'yicha [{new_state}] holatiga o'zgartirildi !"
            else:
                text = 'user_tg_id yoki conversation_name xato !\n' \
                       f'Tip: {command} user_tg_id conversation_name new_state'

            text = f'<pre>{text}</pre>'
            if update.message:
                update.message.reply_html(text)
            else:
                update.edited_message.reply_html(text)


command_handler = CommandHandler(['getuserdata', 'getuserstate', 'updateuserstate', 'getjob'], do_command)
