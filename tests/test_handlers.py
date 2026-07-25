from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from app.handlers.common import Conversation, ConversationStore, register_handlers


class FakeBot:
    def __init__(self) -> None:
        self.message_handlers: list[tuple[dict[str, Any], Any]] = []
        self.callback_handlers: list[Any] = []
        self.messages: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
        self.photos: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
        self.answered_callbacks: list[str] = []

    def message_handler(self, **filters: Any) -> Any:
        def decorator(function: Any) -> Any:
            self.message_handlers.append((filters, function))
            return function

        return decorator

    def callback_query_handler(self, **filters: Any) -> Any:
        del filters

        def decorator(function: Any) -> Any:
            self.callback_handlers.append(function)
            return function

        return decorator

    def send_message(self, *args: Any, **kwargs: Any) -> None:
        self.messages.append((args, kwargs))

    def send_photo(self, *args: Any, **kwargs: Any) -> None:
        self.photos.append((args, kwargs))

    def answer_callback_query(self, callback_id: str) -> None:
        self.answered_callbacks.append(callback_id)


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


def test_callback_selection_is_applied_to_the_clicking_user() -> None:
    bot = FakeBot()
    register_handlers(bot)  # type: ignore[arg-type]
    callback = bot.callback_handlers[0]
    text_handler = handler_for(bot, "text")

    menu_message = user_message(user_id=999)
    call = SimpleNamespace(
        id="callback-1",
        data="qr:phone",
        from_user=SimpleNamespace(id=7, language_code="en"),
        message=menu_message,
    )
    callback(call)
    text_handler(user_message("+1 (202) 555-0123"))

    assert bot.answered_callbacks == ["callback-1"]
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
    callback = bot.callback_handlers[0]
    text_handler = handler_for(bot, "text")
    call = SimpleNamespace(
        id="callback-2",
        data="qr:email",
        from_user=SimpleNamespace(id=7, language_code="en"),
        message=user_message(user_id=999),
    )

    callback(call)
    text_handler(user_message("not-an-email"))
    assert bot.photos == []
    text_handler(user_message("hello@example.com\nHello\nBody"))
    assert len(bot.photos) == 1


def test_shared_location_generates_qr() -> None:
    bot = FakeBot()
    register_handlers(bot)  # type: ignore[arg-type]
    callback = bot.callback_handlers[0]
    location_handler = handler_for(bot, "location")
    callback(
        SimpleNamespace(
            id="callback-3",
            data="qr:geo",
            from_user=SimpleNamespace(id=7, language_code="ru"),
            message=user_message(user_id=999),
        )
    )
    location_handler(
        user_message(
            language="ru",
            location=SimpleNamespace(latitude=55.7558, longitude=37.6176),
        )
    )
    assert len(bot.photos) == 1
    assert bot.photos[0][1]["caption"] == "Готово ✨"


def test_conversation_state_expires_without_background_work() -> None:
    now = 100.0
    store = ConversationStore(ttl_seconds=60, clock=lambda: now)
    message = user_message()
    store.set(message, Conversation("wifi", "en"))
    now = 161.0
    assert store.pop(message) is None
