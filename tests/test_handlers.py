from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from telebot import types

from app.handlers.common import Conversation, ConversationStore, register_handlers


class FakeBot:
    def __init__(self) -> None:
        self.message_handlers: list[tuple[dict[str, Any], Any]] = []
        self.messages: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
        self.photos: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

    def message_handler(self, **filters: Any) -> Any:
        def decorator(function: Any) -> Any:
            self.message_handlers.append((filters, function))
            return function

        return decorator

    def send_message(self, *args: Any, **kwargs: Any) -> None:
        self.messages.append((args, kwargs))

    def send_photo(self, *args: Any, **kwargs: Any) -> None:
        self.photos.append((args, kwargs))


def user_message(
    text: str | None = None,
    *,
    user_id: int = 7,
    language: str = "en",
    location: object | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        chat=SimpleNamespace(id=42),
        from_user=SimpleNamespace(id=user_id, language_code=language),
        text=text,
        location=location,
        message_id=123,
    )


def handler_for(bot: FakeBot, content_type: str) -> Any:
    return next(
        function
        for filters, function in bot.message_handlers
        if filters.get("content_types") == [content_type]
    )


def command_handler(bot: FakeBot, command: str) -> Any:
    return next(
        function
        for filters, function in bot.message_handlers
        if filters.get("commands") == [command]
    )


def test_start_shows_persistent_reply_keyboard() -> None:
    bot = FakeBot()
    register_handlers(bot)  # type: ignore[arg-type]
    command_handler(bot, "start")(user_message("/start", language="ru"))

    keyboard = bot.messages[-1][1]["reply_markup"]
    assert isinstance(keyboard, types.ReplyKeyboardMarkup)
    assert keyboard.resize_keyboard
    assert keyboard.is_persistent
    labels = [button["text"] for row in keyboard.keyboard for button in row]
    assert "📝 Текст / ссылка" in labels
    assert "📶 Wi-Fi" in labels
    assert "✈️ Telegram" in labels


def test_reply_keyboard_selection_is_applied_to_the_user() -> None:
    bot = FakeBot()
    register_handlers(bot)  # type: ignore[arg-type]
    text_handler = handler_for(bot, "text")

    text_handler(user_message("📞 Phone"))
    text_handler(user_message("+1 (202) 555-0123"))

    assert len(bot.photos) == 1
    photo = bot.photos[0][0][1]
    assert photo.name == "qr-code.png"
    assert photo.read(8) == b"\x89PNG\r\n\x1a\n"
    reply = bot.photos[0][1]["reply_parameters"]
    assert reply.message_id == 123
    assert reply.allow_sending_without_reply


def test_invalid_structured_input_can_be_retried() -> None:
    bot = FakeBot()
    register_handlers(bot)  # type: ignore[arg-type]
    text_handler = handler_for(bot, "text")

    text_handler(user_message("✉️ Email"))
    text_handler(user_message("not-an-email"))
    assert bot.photos == []
    text_handler(user_message("hello@example.com\nHello\nBody"))
    assert len(bot.photos) == 1


def test_shared_location_generates_qr() -> None:
    bot = FakeBot()
    register_handlers(bot)  # type: ignore[arg-type]
    text_handler = handler_for(bot, "text")
    location_handler = handler_for(bot, "location")
    text_handler(user_message("📍 Геолокация", language="ru"))
    location_handler(
        user_message(
            language="ru",
            location=SimpleNamespace(latitude=55.7558, longitude=37.6176),
        )
    )
    assert len(bot.photos) == 1
    assert "caption" not in bot.photos[0][1]
    assert "reply_markup" not in bot.photos[0][1]


def test_conversation_state_expires_without_background_work() -> None:
    now = 100.0
    store = ConversationStore(ttl_seconds=60, clock=lambda: now)
    message = user_message()
    store.set(message, Conversation("wifi", "en"))
    now = 161.0
    assert store.pop(message) is None
