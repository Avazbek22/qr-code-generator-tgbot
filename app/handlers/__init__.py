from telebot import types

from app.handlers.common import register_handlers


def configure_commands(bot: object) -> None:
    english = [
        types.BotCommand("start", "Open the QR code menu"),
        types.BotCommand("help", "Show help"),
        types.BotCommand("cancel", "Cancel current input"),
    ]
    russian = [
        types.BotCommand("start", "Открыть меню QR-кодов"),
        types.BotCommand("help", "Показать справку"),
        types.BotCommand("cancel", "Отменить текущий ввод"),
    ]
    bot.set_my_commands(english)  # type: ignore[attr-defined]
    bot.set_my_commands(russian, language_code="ru")  # type: ignore[attr-defined]


__all__ = ["configure_commands", "register_handlers"]
