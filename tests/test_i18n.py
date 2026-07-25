from __future__ import annotations

from app.i18n import text


def test_phone_examples_are_localized() -> None:
    russian = text("ru", "phone")
    english = text("en", "phone")
    assert "+7 (999) 123-45-67" in russian
    assert "+1 (202) 555-0123" in english
    assert russian != english
