from globalvariables import *

PASSENGER_LAYOUT_DICT = {
    "uz": {
        FROM_TEXT: "Qayerdan",
        TO_TEXT: "Qayerga",
        WEIGHT_TEXT: "Yuk og'irligi",
        VOLUME_TEXT: "Yuk hajmi",
        COMMENT_TEXT: "Izoh",
        DATETIME_TEXT: "Ketish vaqti",
        TIME: "hozir",
        USER_TEXT: "E'lon beruvchi",
        USER_PHONE_NUMBER_TEXT: "Tel nomer",
        STATUS_TEXT: "Status",
        OPENED_STATUS: "e'lon ochiq",
        CLOSED_STATUS: "e'lon yopilgan",
        NOT_CONFIRMED_STATUS: "e'lon tasdiqlanmagan",
        TG_ACCOUNT_TEXT: "Telegram akkaunt",
        PASSENGER_TEXT: "Yo'lovchi",
        PASSENGERS_TEXT: "Yo'lovchilar soni"
    },
    "ru": {
        FROM_TEXT: "Откуда",
        TO_TEXT: "Куда",
        WEIGHT_TEXT: "Вес груза",
        VOLUME_TEXT: "Объем груза",
        COMMENT_TEXT: "Примечание",
        DATETIME_TEXT: "Время отправления",
        TIME: "сейчас",
        USER_TEXT: "Объявитель",
        USER_PHONE_NUMBER_TEXT: "Тел номер",
        STATUS_TEXT: "Статус",
        OPENED_STATUS: "объявление открыто",
        CLOSED_STATUS: "объявление закрыто",
        NOT_CONFIRMED_STATUS: "объявление не подтверждено",
        TG_ACCOUNT_TEXT: "Telegram аккаунт",
        PASSENGER_TEXT: "Пассажир",
        PASSENGERS_TEXT: "Количество пассажиров"
    },
    "cy": {
        FROM_TEXT: "Қаердан",
        TO_TEXT: "Қаерга",
        WEIGHT_TEXT: "Юк оғирлиги",
        VOLUME_TEXT: "Юк ҳажми",
        COMMENT_TEXT: "Изоҳ",
        DATETIME_TEXT: "Кетиш вақти",
        TIME: "ҳозир",
        USER_TEXT: "Эълон берувчи",
        USER_PHONE_NUMBER_TEXT: "Тел номер",
        STATUS_TEXT: "Статус",
        OPENED_STATUS: "эълон очиқ",
        CLOSED_STATUS: "эълон ёпилган",
        NOT_CONFIRMED_STATUS: "эълон тасдиқланмаган",
        TG_ACCOUNT_TEXT: "Телеграм аккаунт",
        PASSENGER_TEXT: "Йўловчи",
        PASSENGERS_TEXT: "Йўловчилар сони"
    }
}

PARCEL_LAYOUT_DICT = {
    "uz": {
        PARCEL_TEXT: "Pochta",
        RECEIVER_CONTACT_TEXT: "Qabul qiluvchi",
        SENDER_TEXT: "Yuboruvchi"
    },
    "ru": {
        PARCEL_TEXT: "Почта",
        RECEIVER_CONTACT_TEXT: "Получателя",
        SENDER_TEXT: "Отправитель"
    },
    "cy": {
        PARCEL_TEXT: "Почта",
        RECEIVER_CONTACT_TEXT: "Қабул қилувчи",
        SENDER_TEXT: "Юборувчи"
    },
}

TAXI_LAYOUT_DICT = {
    "uz": {
        TAXI_TEXT: "Taksi",
        EMPTY_SEATS_TEXT: "Bo'sh joylar soni",
        ASK_PARCEL: "Pochta qabul qilinadimi",
        DRIVER_TEXT: "Haydovchi",
        CAR_MODEL: "Mashina markasi",
        BAGGAGE_TEXT: "Bagaj(yuqori bagaj)",
        ALL_DISTRICTS_TEXT: "Barcha tumanlar"

    },
    "ru": {
        TAXI_TEXT: "Такси",
        EMPTY_SEATS_TEXT: "Количество свободных мест",
        ASK_PARCEL: "Будет ли приниматься почта",
        DRIVER_TEXT: "Водитель",
        CAR_MODEL: "Марка машины",
        BAGGAGE_TEXT: "Багаж (верхний багаж)",
        ALL_DISTRICTS_TEXT: "Все районы"

    },
    "cy": {
        TAXI_TEXT: "Такси",
        EMPTY_SEATS_TEXT: "Бўш жойлар сони",
        ASK_PARCEL: "Почта қабул қилинадими",
        DRIVER_TEXT: "Ҳайдовчи",
        CAR_MODEL: "Машина маркаси",
        BAGGAGE_TEXT: "Багаж(юқори багаж)",
        ALL_DISTRICTS_TEXT: "Барча туманлар"

    },
}
USER_INFO_LAYOUT_DICT = {
    'uz': {
        'user_caption_text': "Shaxsiy ma'lumotlar",
        'driver_caption_text': "Haydovchi ma'lumotlari",
        FULLNAME: "Ism, Familya",
        PHONE_NUMBER: "Tel (asosiy)",
        PHONE_NUMBER_2: "Tel (qo'shimcha)",
        UNDEFINED_TEXT: "yo'q",
    },
    'ru': {
        'user_caption_text': "Личные данные",
        'driver_caption_text': "Информация о драйвере",
        FULLNAME: "Исм, Фамиля",
        PHONE_NUMBER: "Тел (основной)",
        PHONE_NUMBER_2: "Тел (дополнительный)",
        UNDEFINED_TEXT: "нет",
    },
    'cy': {
        'user_caption_text': "Шахсий маълумотлар",
        'driver_caption_text': "Ҳайдовчи маълумотлари",
        FULLNAME: "Исм, Фамиля",
        PHONE_NUMBER: "Тел (асосий)",
        PHONE_NUMBER_2: "Тел (қўшимча)",
        UNDEFINED_TEXT: "йўқ",
    }
}

PHONE_NUMBER_LAYOUT_DICT = {
    "uz": {
        1: "Telefon raqamini quyidagi formatda yuboring",
        2: "Misol",
        3: "yoki",
    },
    "ru": {
        1: "Отправьте номер телефона в формате ниже",
        2: "Папример",
        3: "или",
    },
    "cy": {
        1: "Телефон рақамини қуйидаги форматда юборинг",
        2: "Мисол",
        3: "ёки",
    },
}
