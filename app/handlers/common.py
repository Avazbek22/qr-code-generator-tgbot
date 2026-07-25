from __future__ import annotations

import logging
import re
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from qrcode.exceptions import DataOverflowError
from telebot import types

from app.i18n import language_of, text
from app.qr import (
    PayloadError,
    VCard,
    email_payload,
    geo_payload,
    make_png,
    phone_payload,
    sms_payload,
    telegram_payload,
    text_payload,
    vcard_payload,
    wifi_payload,
)

if TYPE_CHECKING:
    from telebot import TeleBot
    from telebot.types import CallbackQuery, Message

LOGGER = logging.getLogger("telegram_bot.handlers")
MODES = (
    "text",
    "wifi",
    "vcard",
    "phone",
    "sms",
    "email",
    "geo",
    "telegram",
)
MODE_SET = frozenset(MODES)


@dataclass(frozen=True, slots=True)
class Conversation:
    mode: str
    language: str


class ConversationStore:
    """Keep only the current input mode in memory; never persist user content."""

    def __init__(
        self,
        *,
        ttl_seconds: int = 15 * 60,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._items: dict[tuple[int, int], tuple[Conversation, float]] = {}
        self._lock = threading.Lock()
        self._ttl_seconds = ttl_seconds
        self._clock = clock

    def _prune(self, now: float) -> None:
        expired = [key for key, (_, deadline) in self._items.items() if deadline <= now]
        for key in expired:
            del self._items[key]

    def set(self, message: Message, conversation: Conversation) -> None:
        self.set_for(message.chat.id, message.from_user.id, conversation)

    def set_for(self, chat_id: int, user_id: int, conversation: Conversation) -> None:
        with self._lock:
            now = self._clock()
            self._prune(now)
            self._items[(chat_id, user_id)] = (
                conversation,
                now + self._ttl_seconds,
            )

    def pop(self, message: Message) -> Conversation | None:
        return self.pop_for(message.chat.id, message.from_user.id)

    def pop_for(self, chat_id: int, user_id: int) -> Conversation | None:
        with self._lock:
            now = self._clock()
            self._prune(now)
            item = self._items.pop((chat_id, user_id), None)
            return item[0] if item is not None else None

    def clear(self, message: Message) -> bool:
        return self.pop(message) is not None

    def clear_for(self, chat_id: int, user_id: int) -> bool:
        return self.pop_for(chat_id, user_id) is not None


def _menu(language: str) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        *[
            types.InlineKeyboardButton(
                text(language, f"button_{mode}"),
                callback_data=f"qr:{mode}",
            )
            for mode in MODES
        ]
    )
    return keyboard


def _again(language: str) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text(language, "again"), callback_data="qr:menu")
    )
    return keyboard


def _split_lines(value: str, size: int) -> list[str]:
    lines = value.replace("\r\n", "\n").split("\n")
    return (lines + [""] * size)[:size]


def _payload(mode: str, value: str) -> str:
    if mode == "text":
        return text_payload(value)
    if mode == "wifi":
        ssid, password, security = _split_lines(value, 3)
        return wifi_payload(ssid, password, security or "WPA")
    if mode == "vcard":
        name, phone, email, organization, title, website, address = _split_lines(
            value, 7
        )
        return vcard_payload(
            VCard(name, phone, email, organization, title, website, address)
        )
    if mode == "phone":
        return phone_payload(value)
    if mode == "sms":
        phone, message = _split_lines(value, 2)
        return sms_payload(phone, message)
    if mode == "email":
        address, subject, body = _split_lines(value, 3)
        return email_payload(address, subject, body)
    if mode == "geo":
        coordinates = re.split(r"[\s,;]+", value.strip())
        if len(coordinates) != 2:
            raise PayloadError("coordinates")
        return geo_payload(*coordinates)
    if mode == "telegram":
        return telegram_payload(value)
    raise PayloadError("mode")


def register_handlers(bot: TeleBot) -> None:
    conversations = ConversationStore()

    def show_menu(message: Message, language: str, *, welcome: bool = False) -> None:
        bot.send_message(
            message.chat.id,
            text(language, "welcome" if welcome else "choose"),
            parse_mode="HTML",
            reply_markup=_menu(language),
        )

    def send_qr(message: Message, payload: str, language: str) -> None:
        try:
            image = make_png(payload)
            bot.send_photo(
                message.chat.id,
                image,
                caption=text(language, "ready"),
                reply_markup=_again(language),
                reply_parameters=types.ReplyParameters(
                    message_id=message.message_id,
                    allow_sending_without_reply=True,
                ),
            )
        except DataOverflowError:
            bot.send_message(message.chat.id, text(language, "too_large"))
        except Exception:
            LOGGER.exception("QR generation or delivery failed")
            bot.send_message(message.chat.id, text(language, "failed"))

    @bot.message_handler(commands=["start"])
    def handle_start(message: Message) -> None:
        conversations.clear(message)
        show_menu(message, language_of(message), welcome=True)

    @bot.message_handler(commands=["help"])
    def handle_help(message: Message) -> None:
        conversations.clear(message)
        language = language_of(message)
        bot.send_message(
            message.chat.id,
            text(language, "help"),
            parse_mode="HTML",
            reply_markup=_menu(language),
        )

    @bot.message_handler(commands=["cancel"])
    def handle_cancel(message: Message) -> None:
        language = language_of(message)
        key = "cancelled" if conversations.clear(message) else "nothing_to_cancel"
        bot.send_message(
            message.chat.id,
            text(language, key),
            reply_markup=_menu(language),
        )

    @bot.callback_query_handler(func=lambda call: bool(call.data))
    def handle_callback(call: CallbackQuery) -> None:
        language = language_of(call)
        data = call.data or ""
        bot.answer_callback_query(call.id)
        if call.message is None:
            return
        if data == "qr:menu":
            conversations.clear_for(call.message.chat.id, call.from_user.id)
            show_menu(call.message, language)
            return
        mode = data.removeprefix("qr:")
        if mode not in MODE_SET:
            return
        conversations.set_for(
            call.message.chat.id,
            call.from_user.id,
            Conversation(mode, language),
        )
        bot.send_message(
            call.message.chat.id,
            text(language, mode),
            parse_mode="HTML",
        )

    @bot.message_handler(content_types=["location"])
    def handle_location(message: Message) -> None:
        conversation = conversations.pop(message)
        if message.location is None:
            return
        if conversation is None:
            send_qr(
                message,
                geo_payload(message.location.latitude, message.location.longitude),
                language_of(message),
            )
            return
        if conversation.mode != "geo":
            conversations.set(message, conversation)
            bot.send_message(message.chat.id, text(conversation.language, "invalid"))
            return
        send_qr(
            message,
            geo_payload(message.location.latitude, message.location.longitude),
            conversation.language,
        )

    @bot.message_handler(
        func=lambda message: bool(message.text),
        content_types=["text"],
    )
    def handle_text(message: Message) -> None:
        if not message.text:
            return
        conversation = conversations.pop(message)
        language = conversation.language if conversation else language_of(message)
        mode = conversation.mode if conversation else "text"
        try:
            payload = _payload(mode, message.text)
        except PayloadError:
            if conversation:
                conversations.set(message, conversation)
                bot.send_message(
                    message.chat.id,
                    text(language, "invalid"),
                    reply_markup=_menu(language),
                )
            else:
                bot.send_message(message.chat.id, text(language, "invalid"))
            return
        send_qr(message, payload, language)
