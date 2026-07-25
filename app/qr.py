from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from io import BytesIO
from urllib.parse import urlencode

import phonenumbers
import qrcode
from phonenumbers import NumberParseException, PhoneNumberFormat
from PIL import ImageOps
from qrcode.constants import ERROR_CORRECT_M


class PayloadError(ValueError):
    """Raised when user input cannot be represented by the selected QR type."""


@dataclass(frozen=True, slots=True)
class VCard:
    name: str
    phone: str = ""
    email: str = ""
    organization: str = ""
    title: str = ""
    website: str = ""
    address: str = ""


def _escape_wifi(value: str) -> str:
    escaped = value.replace("\\", "\\\\")
    for character in ('"', ";", ",", ":"):
        escaped = escaped.replace(character, f"\\{character}")
    return escaped


def _escape_vcard(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace(";", "\\;")
        .replace(",", "\\,")
    )


def text_payload(value: str) -> str:
    value = value.strip()
    if not value:
        raise PayloadError("empty")
    return value


def wifi_payload(
    ssid: str,
    password: str = "",
    security: str = "WPA",
    *,
    hidden: bool = False,
) -> str:
    ssid = ssid.strip()
    if not ssid:
        raise PayloadError("ssid")
    security = security.strip().upper() or "WPA"
    aliases = {"WPA2": "WPA", "WPA3": "WPA", "OPEN": "nopass", "NONE": "nopass"}
    security = aliases.get(security, security)
    if security not in {"WPA", "WEP", "nopass"}:
        raise PayloadError("security")
    if security != "nopass" and not password:
        raise PayloadError("password")
    return (
        f"WIFI:T:{security};S:{_escape_wifi(ssid)};"
        f"P:{_escape_wifi(password)};H:{str(hidden).lower()};;"
    )


def vcard_payload(card: VCard) -> str:
    name = card.name.strip()
    if not name:
        raise PayloadError("name")

    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:;{_escape_vcard(name)};;;",
        f"FN:{_escape_vcard(name)}",
    ]
    if card.organization.strip():
        lines.append(f"ORG:{_escape_vcard(card.organization.strip())}")
    if card.title.strip():
        lines.append(f"TITLE:{_escape_vcard(card.title.strip())}")
    if card.phone.strip():
        lines.append(f"TEL;TYPE=CELL:{normalize_phone(card.phone)}")
    if card.email.strip():
        lines.append(f"EMAIL:{_escape_vcard(card.email.strip())}")
    if card.website.strip():
        lines.append(f"URL:{_escape_vcard(card.website.strip())}")
    if card.address.strip():
        lines.append(f"ADR;TYPE=HOME:;;{_escape_vcard(card.address.strip())};;;;")
    lines.append("END:VCARD")
    return "\r\n".join(lines)


def normalize_phone(value: str) -> str:
    phone = unicodedata.normalize("NFKC", value).strip()
    service_code = re.sub(r"[\s().-]", "", phone)
    if re.fullmatch(r"[*#][0-9*#]{1,31}", service_code):
        return service_code
    if phone.startswith("00"):
        phone = f"+{phone[2:]}"
    try:
        parsed = phonenumbers.parse(phone, None)
    except NumberParseException as exc:
        raise PayloadError("phone") from exc
    if not phonenumbers.is_possible_number(parsed):
        raise PayloadError("phone")
    normalized = phonenumbers.format_number(parsed, PhoneNumberFormat.E164)
    if parsed.extension:
        normalized = f"{normalized};ext={parsed.extension}"
    return normalized


def phone_payload(value: str) -> str:
    return f"tel:{normalize_phone(value)}"


def sms_payload(phone: str, message: str = "") -> str:
    return f"SMSTO:{normalize_phone(phone)}:{message.strip()}"


def email_payload(address: str, subject: str = "", body: str = "") -> str:
    address = address.strip()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", address):
        raise PayloadError("email")
    fields = {"subject": subject, "body": body}
    query = urlencode({key: value for key, value in fields.items() if value})
    return f"mailto:{address}" + (f"?{query}" if query else "")


def geo_payload(latitude: str | float, longitude: str | float) -> str:
    try:
        lat = float(latitude)
        lon = float(longitude)
    except (TypeError, ValueError) as exc:
        raise PayloadError("coordinates") from exc
    if not -90 <= lat <= 90 or not -180 <= lon <= 180:
        raise PayloadError("coordinates")
    return f"geo:{lat:.7f},{lon:.7f}".replace(".0000000", "")


def telegram_payload(value: str) -> str:
    value = value.strip()
    value = re.sub(r"^https?://(?:www\.)?(?:t\.me|telegram\.me)/", "", value)
    value = value.split("?", 1)[0].strip("/")
    if value.startswith("@"):
        value = value[1:]
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{4,31}", value):
        raise PayloadError("telegram")
    return f"https://t.me/{value}"


def make_png(payload: str) -> BytesIO:
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_M,
        box_size=24,
        border=0,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    image = ImageOps.expand(image, border=24, fill="white")

    output = BytesIO()
    output.name = "qr-code.png"
    image.save(output, format="PNG", optimize=True)
    output.seek(0)
    return output
