from .inlinekeyboardvariables import *

inline_keyboard_types = {

    langs_keyboard: [
        {
            "text": "O'zbekcha (lotin)",
            "icon": "🇺🇿",
            "data": "uz"
        },
        {
            "text": "Русский",
            "icon": "🇷🇺",
            "data": "ru"
        },
        {
            "text": "Ўзбекча (кирилл)",
            "icon": "🇺🇿",
            "data": "cy"
        },
    ],

    back_next_keyboard: [
        {
            "text_uz": "Ortga",
            "text_ru": "Назад",
            "text_cy": "Ортга",
            "icon": "«",
            "data": "back"
        },
        {
            "text_uz": "Keyingisi",
            "text_ru": "Следующий",
            "text_cy": "Кейингиси",
            "icon": "»",
            "data": "next"
        },

    ],

    confirm_keyboard: [
        {
            "text_uz": "Tasdiqlash",
            "text_ru": "Подтвердить",
            "text_cy": "Тасдиқлаш",
            "icon": "✅",
            "data": "confirm"
        },
        {
            "text_uz": "Bekor qilish",
            "text_ru": "Отменить",
            "text_cy": "Бекор қилиш",
            "icon": "❌",
            "data": "cancel"
        },
    ],

    order_keyboard: {
        "uz": {1: "Buyurtma berish", 2: "Ortga"},
        "cy": {
            1: "Манзилни таҳрирлаш",
            2: "Юк маълумотларини таҳрирлаш",
            3: "Кун ва вақтни таҳрирлаш",
            4: "Таҳрирни якунлаш",
        },
        "ru": {
            1: "Редактировать адрес",
            2: "Редактировать информацию о грузе",
            3: "Редактировать дату и время",
            4: "Закончить редактирование",

        },
    },

    orders_keyboard: {
        "uz": {1: "Qabul qilish", 2: "Rad etish"},
        "cy": {
            1: "Манзилни таҳрирлаш",
            2: "Юк маълумотларини таҳрирлаш",
            3: "Кун ва вақтни таҳрирлаш",
            4: "Таҳрирни якунлаш",
        },
        "ru": {
            1: "Редактировать адрес",
            2: "Редактировать информацию о грузе",
            3: "Редактировать дату и время",
            4: "Закончить редактирование",

        },
    },

    yes_no_keyboard: [
        {
            "text_uz": "Ha",
            "text_ru": "Да",
            "text_cy": "Ҳа",
            "icon": "✅",
            "data": "yes"
        },
        {
            "text_uz": "Yo'q",
            "text_ru": "Нет",
            "text_cy": "Йўқ",
            "icon": "❌",
            "data": "no"
        },
    ],

    basket_keyboard: {
        "uz": {1: "Buyurtmani davom ettirish", 2: "Buyurtmani tasdiqlash"},
        "cy": ["Эълонни ёпиш", "Эълонни қайта очиш", "Эълонни қайта очилди"],
        "ru": ["Закрыть объявление", "Повторно открыть объявление", "Объявление было повторно открыто"],

    },

    dates_keyboard: [
        {
            "text_uz": "Hozir",
            "text_ru": "Сейчас",
            "text_cy": "Ҳозир",
            "icon": "",
            "data": "now"
        },
        {
            "text_uz": "Bugun",
            "text_ru": "Сегодня",
            "text_cy": "Бугун",
            "icon": "",
            "data": "today"
        },
    ]
}
