from DB import get_user


def set_user_data(user_id, user_data):
    value = user_data.setdefault('user_data', None)

    if not value:
        value = get_user(user_id)

        if value:
            value.pop('created_at')
            value.pop('updated_at')

        user_data['user_data'] = value


def wrap_tags(*args):
    symbol = ' ' if len(args) > 1 else ''

    return f'<b><i><u>{symbol.join(args)}</u></i></b>'


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
