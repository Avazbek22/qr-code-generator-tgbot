from __future__ import annotations

import logging
from pathlib import Path

from app.logging_setup import configure_logging

TOKEN = "123456789:abcdefghijklmnopqrstuvwxyzABCDE"


def test_logging_redacts_token_and_keeps_traceback_in_file(
    tmp_path: Path, capsys: object
) -> None:
    logger = configure_logging(tmp_path, "INFO")
    try:
        raise RuntimeError(f"failure near {TOKEN}")
    except RuntimeError:
        logger.exception("request used %s", TOKEN)

    for handler in logging.getLogger().handlers:
        handler.flush()
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    log_text = (tmp_path / "bot.log").read_text(encoding="utf-8")
    assert TOKEN not in captured.out
    assert TOKEN not in log_text
    assert "<bot-token-redacted>" in captured.out
    assert "Traceback" not in captured.out
    assert "Traceback" in log_text


def test_debug_level_does_not_enable_telegram_request_logging(tmp_path: Path) -> None:
    configure_logging(tmp_path, "DEBUG")
    assert logging.getLogger("telegram_bot").getEffectiveLevel() == logging.DEBUG
    assert logging.getLogger("TeleBot").getEffectiveLevel() == logging.WARNING
    assert logging.getLogger("urllib3").getEffectiveLevel() == logging.WARNING
