from __future__ import annotations

from typing import Any

TEXTS: dict[str, dict[str, str]] = {
    "ru": {
        "welcome": (
            "<b>QR-код — за пару секунд</b>\n\n"
            "Выберите готовый формат ниже или просто отправьте мне текст или ссылку. "
            "Я верну обычный чёрно-белый QR-код в PNG.\n\n"
            "🔒 Ничего не сохраняется."
        ),
        "help": (
            "<b>Как пользоваться</b>\n\n"
            "• Отправьте текст или ссылку — QR появится сразу.\n"
            "• Для Wi-Fi, контакта, телефона, SMS, email, геолокации или Telegram "
            "выберите кнопку в меню.\n"
            "• /cancel отменяет текущий ввод, /start открывает меню.\n\n"
            "Бот не ведёт историю и не хранит содержимое QR-кодов."
        ),
        "choose": "Что зашифруем?",
        "text": "Отправьте текст или ссылку одним сообщением.",
        "wifi": (
            "Отправьте данные Wi-Fi в трёх строках:\n"
            "<code>Название сети\nПароль\nWPA</code>\n\n"
            "Третья строка: <code>WPA</code>, <code>WEP</code> или "
            "<code>nopass</code> для открытой сети."
        ),
        "vcard": (
            "Отправьте контакт — по одному полю в строке:\n"
            "<code>Имя\nТелефон\nEmail\nКомпания\nДолжность\nСайт\nАдрес</code>\n\n"
            "Только имя обязательно. Пустые необязательные строки можно оставить."
        ),
        "phone": "Отправьте номер телефона, например <code>+79991234567</code>.",
        "sms": (
            "Первая строка — номер, вторая — текст SMS:\n"
            "<code>+79991234567\nБуду через 10 минут</code>"
        ),
        "email": (
            "Отправьте email, тему и текст — каждый с новой строки:\n"
            "<code>hello@example.com\nПривет\nТекст письма</code>"
        ),
        "geo": (
            "Отправьте геолокацию через 📎 или координаты через пробел:\n"
            "<code>55.7558 37.6176</code>"
        ),
        "telegram": (
            "Отправьте <code>@username</code> или ссылку <code>t.me/username</code>."
        ),
        "cancelled": "Готово, ввод отменён.",
        "nothing_to_cancel": "Сейчас нечего отменять.",
        "invalid": (
            "Не получилось разобрать данные. Проверьте пример и попробуйте ещё раз."
        ),
        "too_large": "Слишком много данных для одного QR-кода. Сократите текст.",
        "failed": "Не удалось создать QR-код. Попробуйте ещё раз.",
        "button_text": "📝 Текст / ссылка",
        "button_wifi": "📶 Wi-Fi",
        "button_vcard": "👤 Контакт",
        "button_phone": "📞 Телефон",
        "button_sms": "💬 SMS",
        "button_email": "✉️ Email",
        "button_geo": "📍 Геолокация",
        "button_telegram": "✈️ Telegram",
    },
    "en": {
        "welcome": (
            "<b>A QR code in seconds</b>\n\n"
            "Choose a format below, or simply send me any text or link. "
            "I will return a clean black-and-white PNG QR code.\n\n"
            "🔒 Nothing is stored."
        ),
        "help": (
            "<b>How it works</b>\n\n"
            "• Send text or a link to get a QR code instantly.\n"
            "• Use the menu for Wi-Fi, contacts, phone, SMS, email, location, "
            "or Telegram.\n"
            "• /cancel stops the current input; /start opens the menu.\n\n"
            "The bot keeps no history and stores no QR contents."
        ),
        "choose": "What should the QR code contain?",
        "text": "Send the text or link in one message.",
        "wifi": (
            "Send Wi-Fi details on three lines:\n"
            "<code>Network name\nPassword\nWPA</code>\n\n"
            "The third line can be <code>WPA</code>, <code>WEP</code>, or "
            "<code>nopass</code> for an open network."
        ),
        "vcard": (
            "Send one contact field per line:\n"
            "<code>Name\nPhone\nEmail\nCompany\nJob title\nWebsite\nAddress</code>\n\n"
            "Only the name is required. Optional lines may be empty."
        ),
        "phone": "Send a phone number, for example <code>+12025550123</code>.",
        "sms": (
            "Put the number on the first line and SMS text on the second:\n"
            "<code>+12025550123\nSee you in 10 minutes</code>"
        ),
        "email": (
            "Send the email address, subject, and body on separate lines:\n"
            "<code>hello@example.com\nHello\nEmail body</code>"
        ),
        "geo": (
            "Share a location via 📎 or send coordinates separated by a space:\n"
            "<code>40.7128 -74.0060</code>"
        ),
        "telegram": "Send <code>@username</code> or a <code>t.me/username</code> link.",
        "cancelled": "Done, input cancelled.",
        "nothing_to_cancel": "There is nothing to cancel right now.",
        "invalid": "I could not read that. Check the example and try again.",
        "too_large": "That is too much data for one QR code. Please shorten it.",
        "failed": "I could not create the QR code. Please try again.",
        "button_text": "📝 Text / link",
        "button_wifi": "📶 Wi-Fi",
        "button_vcard": "👤 Contact",
        "button_phone": "📞 Phone",
        "button_sms": "💬 SMS",
        "button_email": "✉️ Email",
        "button_geo": "📍 Location",
        "button_telegram": "✈️ Telegram",
    },
}


def language_of(source: Any) -> str:
    user = getattr(source, "from_user", None)
    code = getattr(user, "language_code", "") or ""
    return "ru" if code.lower().startswith("ru") else "en"


def text(language: str, key: str) -> str:
    return TEXTS.get(language, TEXTS["en"])[key]
