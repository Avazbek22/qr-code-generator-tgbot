from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image

from app.qr import (
    PayloadError,
    VCard,
    email_payload,
    geo_payload,
    make_png,
    phone_payload,
    sms_payload,
    telegram_payload,
    vcard_payload,
    wifi_payload,
)


def test_wifi_payload_escapes_reserved_characters() -> None:
    payload = wifi_payload("Cafe;Guest", "secret:word", "WPA2")
    assert payload == r"WIFI:T:WPA;S:Cafe\;Guest;P:secret\:word;H:false;;"


def test_open_wifi_does_not_require_password() -> None:
    assert wifi_payload("Free WiFi", security="open") == (
        "WIFI:T:nopass;S:Free WiFi;P:;H:false;;"
    )


def test_vcard_contains_only_provided_fields() -> None:
    payload = vcard_payload(
        VCard(
            name="Ada Lovelace",
            phone="+44 20 7946 0958",
            email="ada@example.com",
            organization="Analytical Engines",
        )
    )
    assert payload.startswith("BEGIN:VCARD\r\nVERSION:3.0")
    assert "FN:Ada Lovelace" in payload
    assert "TEL;TYPE=CELL:+442079460958" in payload
    assert "EMAIL:ada@example.com" in payload
    assert payload.endswith("END:VCARD")
    assert "TITLE:" not in payload


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("+7 (999) 123-45-67", "tel:+79991234567"),
        ("0044 20 7946 0958", "tel:+442079460958"),
        ("＋８１ ３－１２３４－５６７８", "tel:+81312345678"),  # noqa: RUF001
        ("+49 (30) 901820 ext. 42", "tel:+4930901820;ext=42"),
        ("*123#", "tel:*123#"),
    ],
)
def test_phone_formats_are_normalized_internationally(
    value: str, expected: str
) -> None:
    assert phone_payload(value) == expected


@pytest.mark.parametrize(
    ("function", "expected"),
    [
        (lambda: phone_payload("+1 (202) 555-0123"), "tel:+12025550123"),
        (
            lambda: sms_payload("+1 202 555 0123", "Hello"),
            "SMSTO:+12025550123:Hello",
        ),
        (
            lambda: email_payload("hello@example.com", "Hello world", "Text"),
            "mailto:hello@example.com?subject=Hello+world&body=Text",
        ),
        (lambda: geo_payload("55.7558", "37.6176"), "geo:55.7558000,37.6176000"),
        (
            lambda: telegram_payload("https://t.me/example_bot?start=ignored"),
            "https://t.me/example_bot",
        ),
    ],
)
def test_typed_payloads(function: object, expected: str) -> None:
    assert function() == expected  # type: ignore[operator]


@pytest.mark.parametrize(
    "function",
    [
        lambda: wifi_payload("", "password"),
        lambda: phone_payload("call-me"),
        lambda: phone_payload("202-555-0123"),
        lambda: phone_payload("+999 123 456"),
        lambda: email_payload("not-an-email"),
        lambda: geo_payload(91, 0),
        lambda: telegram_payload("@bad"),
    ],
)
def test_invalid_payloads_are_rejected(function: object) -> None:
    with pytest.raises(PayloadError):
        function()  # type: ignore[operator]


def test_png_is_generated_in_memory() -> None:
    image = make_png("hello")
    assert isinstance(image, BytesIO)
    assert image.name == "qr-code.png"
    assert image.tell() == 0
    assert image.read(8) == b"\x89PNG\r\n\x1a\n"
    image.seek(0)
    with Image.open(image) as qr_image:
        assert qr_image.mode == "RGB"
        assert qr_image.size == (552, 552)
        assert qr_image.getpixel((23, 23)) == (255, 255, 255)
        assert qr_image.getpixel((24, 24)) == (0, 0, 0)
