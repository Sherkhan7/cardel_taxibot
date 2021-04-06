from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from DB import *
from .inlinekeyboardtypes import *
import datetime


class InlineKeyboard(object):
    def __init__(self, keyb_type, lang=None, data=None, history=None):

        self.__type = keyb_type
        self.__lang = lang
        self.__data = data
        self.__history = history
        self.__keyboard = self.__create_inline_keyboard(self.__type, self.__lang, self.__data, self.__history)

    def __create_inline_keyboard(self, keyb_type, lang, data, history):

        if keyb_type == langs_keyboard:
            return self.__get_langs_keyboard(inline_keyboard_types[keyb_type])

        elif keyb_type == regions_keyboard:
            return self.__get_regions_keyboard(get_all_regions(), keyb_type, lang)

        elif keyb_type == districts_keyboard:
            return self.__get_regions_keyboard(get_districts_by_parent(data), keyb_type, lang)

        elif keyb_type == districts_selective_keyboard:
            re_check_list = None
            if isinstance(data, dict):
                re_check_list = list(data.values())[0]
                data = list(data.keys())[0]
            return self.__get_districts_selective_keyboard(get_districts_by_parent(data), lang,
                                                           re_check_list=re_check_list)

        elif keyb_type == dates_keyboard:
            return self.__get_dates_keyboard(inline_keyboard_types[keyb_type], lang)

        elif keyb_type == times_keyboard:
            return self.__get_hours_keyboard(lang, data)

        elif keyb_type == confirm_keyboard:
            return self.__get_confirm_keyboard(inline_keyboard_types[keyb_type], lang)

        elif keyb_type == orders_keyboard:
            return self.__get_orders_keyboard(inline_keyboard_types[keyb_type][lang], data)

        elif keyb_type == yes_no_keyboard:
            return self.__get_yes_no_keyboard(inline_keyboard_types[keyb_type], lang)

        elif keyb_type == car_models_keyboard:
            return self.__get_car_models_keyboard(get_car_models())

        elif keyb_type == paginate_keyboard:
            return self.__get_paginate_keyboard(data, history)

        elif keyb_type == geo_keyboard:
            return self.__get_geo_keyboard(data)

    @staticmethod
    def __get_langs_keyboard(buttons):

        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f'{buttons[0]["icon"]} {buttons[0]["text"]}', callback_data=buttons[0]["data"])],
            [InlineKeyboardButton(f'{buttons[1]["icon"]} {buttons[1]["text"]}', callback_data=buttons[1]["data"])],
            [InlineKeyboardButton(f'{buttons[2]["icon"]} {buttons[2]["text"]}', callback_data=buttons[2]["data"])],
        ])

    @staticmethod
    def __get_regions_keyboard(regions, keyb_type, lang):
        length = len(regions)
        icon = inline_keyboard_types[back_next_keyboard][0]['icon']
        back_btn_text = inline_keyboard_types[back_next_keyboard][0][f'text_{lang}']
        back_btn_text = f'{icon} {back_btn_text}'
        back_btn_data = inline_keyboard_types[back_next_keyboard][0]['data']

        if length % 2 == 0:

            keyboard = [
                [
                    InlineKeyboardButton(regions[i][f'name_{lang}'], callback_data=regions[i]['id']),
                    InlineKeyboardButton(regions[i + 1][f'name_{lang}'], callback_data=regions[i + 1]['id'])
                ]
                for i in range(0, length, 2)
            ]

            if keyb_type == districts_keyboard:
                keyboard.append([InlineKeyboardButton(back_btn_text, callback_data=back_btn_data)])
        else:

            keyboard = [
                [
                    InlineKeyboardButton(regions[i][f'name_{lang}'], callback_data=regions[i]['id']),
                    InlineKeyboardButton(back_btn_text, callback_data=back_btn_data)
                ]
                if i == length - 1 else
                [
                    InlineKeyboardButton(regions[i][f'name_{lang}'], callback_data=regions[i]['id']),
                    InlineKeyboardButton(regions[i + 1][f'name_{lang}'], callback_data=regions[i + 1]['id'])
                ] for i in range(0, length, 2)
            ]

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def __get_districts_selective_keyboard(regions, lang, re_check_list):
        length = len(regions)
        back_btn_icon = inline_keyboard_types[back_next_keyboard][0]['icon']
        back_btn_text = inline_keyboard_types[back_next_keyboard][0][f'text_{lang}']
        back_btn_text = f'{back_btn_icon} {back_btn_text}'
        back_btn_data = inline_keyboard_types[back_next_keyboard][0]['data']

        check_all_btn_icon = inline_keyboard_types[districts_selective_keyboard][0]['icon']
        check_all_btn_text = inline_keyboard_types[districts_selective_keyboard][0][f'text_{lang}']
        check_all_btn_text = f'{check_all_btn_icon} {check_all_btn_text}'
        check_all_btn_data = inline_keyboard_types[districts_selective_keyboard][0][f'data']

        save_btn_icon = inline_keyboard_types[districts_selective_keyboard][1]['icon']
        save_btn_text = inline_keyboard_types[districts_selective_keyboard][1][f'text_{lang}']
        save_btn_text = f'{save_btn_icon} {save_btn_text}'
        save_btn_data = inline_keyboard_types[districts_selective_keyboard][1]['data']

        ok_btn_icon = inline_keyboard_types[districts_selective_keyboard][2]['icon']
        ok_btn_text = inline_keyboard_types[districts_selective_keyboard][2][f'text_{lang}']
        ok_btn_text = f'{ok_btn_icon} {ok_btn_text}'
        ok_btn_data = inline_keyboard_types[districts_selective_keyboard][2]['data']

        icon = '☑'
        _data = '_unchecked'
        recheck = True

        if re_check_list and len(re_check_list) == len(regions):
            icon = '✅'
            _data = '_checked'
            recheck = False

        if length % 2 == 0:

            keyboard = [
                [
                    InlineKeyboardButton(f'{icon} ' + regions[i][f'name_{lang}'],
                                         callback_data=str(regions[i]['id']) + _data),
                    InlineKeyboardButton(f'{icon} ' + regions[i + 1][f'name_{lang}'],
                                         callback_data=str(regions[i + 1]['id']) + _data)
                ]
                for i in range(0, length, 2)
            ]

            keyboard.append([InlineKeyboardButton(back_btn_text, callback_data=back_btn_data)])
        else:

            keyboard = [
                [
                    InlineKeyboardButton(f'{icon} ' + regions[i][f'name_{lang}'],
                                         callback_data=str(regions[i]['id']) + _data),
                    InlineKeyboardButton(back_btn_text, callback_data=back_btn_data)
                ]
                if i == length - 1 else
                [
                    InlineKeyboardButton(f'{icon} ' + regions[i][f'name_{lang}'],
                                         callback_data=str(regions[i]['id']) + _data),
                    InlineKeyboardButton(f'{icon} ' + regions[i + 1][f'name_{lang}'],
                                         callback_data=str(regions[i + 1]['id']) + _data)
                ] for i in range(0, length, 2)
            ]

        if re_check_list and recheck:
            for i in re_check_list:
                stop = False
                for row in keyboard:
                    for col in row:
                        if col.callback_data != 'back':
                            text = col.text.split(maxsplit=1)[-1]
                            _data = col.callback_data.split('_')
                            district_id = int(_data[0])
                            new_action = "checked"
                            new_icon = "✅"
                            if i == district_id:
                                col.text = f"{new_icon} {text}"
                                col.callback_data = f'{district_id}_{new_action}'
                                stop = True
                                break
                    if stop:
                        break

        keyboard.insert(0, [InlineKeyboardButton(check_all_btn_text, callback_data=check_all_btn_data)])

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def __get_book_keyboard(buttons, book_data):

        button1_text = f'\U0001F4D6  {buttons[1]}'
        button1_url = book_data['description_url']

        button2_text = f'\U0001F4E6  {buttons[2]}'
        button2_data = 'ordering'

        button3_text = f'\U00002B05  {buttons[3]}'
        button3_data = 'back'

        inline_keyboard = [
            [InlineKeyboardButton(button2_text, callback_data=button2_data)],
            [InlineKeyboardButton(button3_text, callback_data=button3_data)],
        ]

        if book_data['description_url']:
            inline_keyboard.insert(0, [
                InlineKeyboardButton(button1_text, url=button1_url)
            ])

        return InlineKeyboardMarkup(inline_keyboard)

    @staticmethod
    def __get_dates_keyboard(buttons, lang):

        # now
        button1_text = buttons[0][f'text_{lang}']
        button1_data = buttons[0]['data']
        # today
        today = datetime.datetime.today()
        button2_text = buttons[1][f'text_{lang}']
        button2_data = today.strftime("%d-%m-%Y")
        # tomorrow
        tomorrow = today + datetime.timedelta(days=1)
        button3_text = tomorrow.strftime("%d-%m-%Y")
        button3_data = button3_text
        # after tomorrow
        after_tomorrow = tomorrow + datetime.timedelta(days=1)
        button4_text = after_tomorrow.strftime("%d-%m-%Y")
        button4_data = button4_text

        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(button1_text, callback_data=button1_data),
                InlineKeyboardButton(button2_text, callback_data=button2_data)
            ],
            [
                InlineKeyboardButton(button3_text, callback_data=button3_data),
                InlineKeyboardButton(button4_text, callback_data=button4_data)
            ]
        ])

    @staticmethod
    def __get_hours_keyboard(lang, data):
        begin = data['begin']
        end = data['end']

        if begin == 6 and end == 17:
            icon = inline_keyboard_types[back_next_keyboard][1]['icon']
            text = inline_keyboard_types[back_next_keyboard][1][f'text_{lang}']
            button_text = f'{text} {icon}'
            button_data = inline_keyboard_types[back_next_keyboard][1]['data']

            inline_keyboard = [
                [
                    InlineKeyboardButton(f'{i}:00', callback_data=f'{i}:00'),
                    InlineKeyboardButton(f'{i + 1}:00', callback_data=f'{i + 1}:00'),
                    InlineKeyboardButton(f'{i + 2}:00', callback_data=f'{i + 2}:00'),
                ] for i in range(begin, end + 1, 3)
            ]

        elif begin == 18 and end == 29:
            inline_keyboard = []
            icon = inline_keyboard_types[back_next_keyboard][0]['icon']
            text = inline_keyboard_types[back_next_keyboard][0][f'text_{lang}']
            button_text = f'{icon} {text}'
            button_data = inline_keyboard_types[back_next_keyboard][0]['data']

            for i in range(begin, end + 1, 3):

                if i == 24:
                    i = 0
                elif i == 27:
                    i = 3

                inline_keyboard.append([
                    InlineKeyboardButton(f'{i}:00', callback_data=f'{i}:00'),
                    InlineKeyboardButton(f'{i + 1}:00', callback_data=f'{i + 1}:00'),
                    InlineKeyboardButton(f'{i + 2}:00', callback_data=f'{i + 2}:00'),

                ])

        inline_keyboard.append([InlineKeyboardButton(button_text, callback_data=button_data)])

        return InlineKeyboardMarkup(inline_keyboard)

    @staticmethod
    def __get_confirm_keyboard(buttons, lang):
        text = buttons[0][f'text_{lang}']
        icon = buttons[0]['icon']
        button1_text = f'{icon} {text}'
        button1_data = buttons[0]['data']

        text = buttons[1][f'text_{lang}']
        icon = buttons[1]['icon']
        button2_text = f'{icon} {text}'
        button2_data = buttons[1]['data']

        return InlineKeyboardMarkup([
            [InlineKeyboardButton(button1_text, callback_data=button1_data)],
            [InlineKeyboardButton(button2_text, callback_data=button2_data)]
        ])

    @staticmethod
    def __get_orders_keyboard(buttons, data):

        inline_keyboard = []
        button1_text = f"\U0001F3C1 Manzilni xaritadan ko'rish"

        if data[0]:
            from_latitude = data[0]['latitude']
            from_longitude = data[0]['longitude']
            inline_keyboard.append(
                [InlineKeyboardButton(button1_text,
                                      url=f'http://www.google.com/maps/place/{from_latitude},{from_longitude}/'
                                          f'@{from_latitude},{from_longitude},12z')])

        button2_text = f'\U00002705 {buttons[1]}'
        button3_text = f'\U0000274C {buttons[2]}'

        inline_keyboard.extend([
            [InlineKeyboardButton(button2_text, callback_data=f'r_{data[-1]}')],
            [InlineKeyboardButton(button3_text, callback_data=f'c_{data[-1]}')]
        ])

        return InlineKeyboardMarkup(inline_keyboard)

    @staticmethod
    def __get_geo_keyboard(data):
        button2_text = f"\U0001F3C1 Manzilni xaritadan ko'rish"

        from_latitude = data['latitude']
        from_longitude = data['longitude']

        return InlineKeyboardMarkup([
            [InlineKeyboardButton(button2_text,
                                  url=f'http://www.google.com/maps/place/{from_latitude},{from_longitude}/'
                                      f'@{from_latitude},{from_longitude},12z')]
        ])

    @staticmethod
    def __get_yes_no_keyboard(buttons, lang):
        # yes
        text = buttons[0][f'text_{lang}']
        icon = buttons[0]['icon']
        button1_text = f'{icon} {text}'
        button1_data = buttons[0]['data']

        # no
        text = buttons[1][f'text_{lang}']
        icon = buttons[1]['icon']
        button2_text = f'{icon} {text}'
        button2_data = buttons[1]['data']

        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(button1_text, callback_data=button1_data),
                InlineKeyboardButton(button2_text, callback_data=button2_data)
            ],
        ])

    @staticmethod
    def __get_car_models_keyboard(car_models):
        length = len(car_models)
        if length % 2 == 0:

            keyboard = [
                [
                    InlineKeyboardButton(car_models[i]['car_model'], callback_data=car_models[i]['id']),
                    InlineKeyboardButton(car_models[i + 1]['car_model'], callback_data=car_models[i + 1]['id'])
                ]
                for i in range(0, length, 2)
            ]

        else:
            keyboard = [
                [
                    InlineKeyboardButton(car_models[i]['car_model'], callback_data=car_models[i]['id'])
                ]
                if i == length - 1 else
                [
                    InlineKeyboardButton(car_models[i]['car_model'], callback_data=car_models[i]['id']),
                    InlineKeyboardButton(car_models[i + 1]['car_model'], callback_data=car_models[i + 1]['id'])
                ] for i in range(0, length, 2)
            ]

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def __get_paginate_keyboard(data, history=None):

        wanted, orders = data
        length = len(orders)

        state = 'h_' if history else ''

        if wanted == 1 and length == 1:
            button1_text = '.'
            button1_data = 'dot_1'

            button3_text = '.'
            button3_data = 'dot_2'

        elif wanted == 1 and length > 1:
            button1_text = '.'
            button1_data = 'dot'

            button3_text = '\U000023E9'
            button3_data = f'{state}w_{wanted + 1}'

        elif wanted == length:
            button1_text = '\U000023EA'
            button1_data = f'{state}w_{wanted - 1}'

            button3_text = '.'
            button3_data = 'dot'

        else:
            button1_text = '\U000023EA'
            button1_data = f'{state}w_{wanted - 1}'

            button3_text = '\U000023E9'
            button3_data = f'{state}w_{wanted + 1}'

        button2_text = f'{wanted}/{length}'
        button2_data = 'None'

        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(button1_text, callback_data=button1_data),
                InlineKeyboardButton(button2_text, callback_data=button2_data),
                InlineKeyboardButton(button3_text, callback_data=button3_data),
            ],
        ])

    def get_keyboard(self):

        return self.__keyboard
