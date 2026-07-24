# Contributing

Thanks for helping make QR Code Generator Telegram Bot better.

The project has a narrow promise: a pleasant self-hosted QR bot that stays
small, private, and easy to fork. Focused bug fixes, translations, payload
compatibility improvements, accessibility work, tests, and documentation are
welcome.

Please avoid changes that require a hosted service, database, analytics,
advertising, accounts, or a large background worker stack. Optional downstream
forks are a better home for those features.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Run the checks before opening a pull request:

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest
shellcheck install.sh scripts/*.sh tests/shell/*.sh
bash tests/shell/test-deploy.sh
ENV_FILE=.env-example APP_SLUG=qr-code-generator-tgbot \
  docker compose config --quiet
```

Production shell changes should include fake-command coverage for both success
and failure paths. QR formats should include unit tests for valid, escaped, and
invalid input.

Never use a real Telegram token or private QR contents in tests, screenshots,
issues, or logs. Open a focused pull request and describe any deployment or
rollback impact.

By contributing, you agree that your contribution is licensed under the MIT
License.
