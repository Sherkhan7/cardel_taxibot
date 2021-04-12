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
        {
            "text_uz": "noma'lum",
            "text_ru": "неизвестно",
            "text_cy": "номаълум",
            "icon": "❓",
            "data": "undefined"
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
        {
            "text_uz": "Bor",
            "text_ru": "Есть",
            "text_cy": "Бор",
            "icon": "✅",
            "data": "have"
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
    ],

    districts_selective_keyboard: [
        {
            "text_uz": "Barchasini tanlash",
            "text_ru": "Выбрать все",
            "text_cy": "Барчасини танлаш",
            "icon": "✅",
            "data": "check_all"
        },
        {
            "text_uz": "Saqlash",
            "text_ru": "Сохранить",
            "text_cy": "Сақлаш",
            "icon": "♻️",
            "data": "save_checked"
        },
        {
            "text_uz": "Yakunlash",
            "text_ru": "Завершение",
            "text_cy": "Якунлаш",
            "icon": "🆗",
            "data": "ok"
        },

    ],

    edit_keyboard: [
        {
            "text_uz": "\"Qayerdan\"ni tahrirlash",
            "text_ru": "Редактировать \"Откуда\"",
            "text_cy": "\"Қаердан\"ни таҳрирлаш",
            "icon": "✏",
            "data": "edit_from"
        },
        {
            "text_uz": "\"Qayerga\"ni tahrirlash",
            "text_ru": "Редактировать \"Куда\"",
            "text_cy": "\"Қаерга\"ни таҳрирлаш",
            "icon": "✏",
            "data": "edit_to"
        },
        {
            "text_uz": "Bo'sh joyni tahrirlash",
            "text_ru": "Редактировать свободных мест",
            "text_cy": "Бўш жойни таҳрирлаш",
            "icon": "✏",
            "data": "edit_empty_seats"
        },
        {
            "text_uz": "Pochtani tahrirlash",
            "text_ru": "Редактировать почту",
            "text_cy": "Почтани таҳрирлаш",
            "icon": "✏",
            "data": "edit_ask_parcel"
        },
        {
            "text_uz": "Kun va vaqtni tahrirlash",
            "text_ru": "Изменить дату и время",
            "text_cy": "Кун ва вақтни таҳрирлаш",
            "icon": "✏",
            "data": "edit_datetime"
        },
        {
            "text_uz": "Izohni tahrirlash",
            "text_ru": "Редактировать комментарий",
            "text_cy": "Изоҳни таҳрирлаш",
            "icon": "✏",
            "data": "edit_comment"
        },

    ],
}
