<div align="center">

![QR Code Generator Telegram Bot](docs/assets/qr-bot-banner.png)

# QR Code Generator Telegram Bot

**A small, private, self-hosted Telegram bot that turns everyday data into
ready-to-use PNG QR codes.**

[![CI](https://github.com/Avazbek22/qr-code-generator-tgbot/actions/workflows/ci.yml/badge.svg)](https://github.com/Avazbek22/qr-code-generator-tgbot/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![No database](https://img.shields.io/badge/database-none-6C757D)](#privacy-by-design)

[Русская версия](docs/README.ru.md) ·
[Quick start](#quick-start) ·
[Features](#everything-you-actually-need) ·
[Contributing](CONTRIBUTING.md)

</div>

---

Sometimes you need a QR code right now—not another account, dashboard, ad,
watermark, or subscription. This bot lives in Telegram, creates a clean PNG,
sends it back, and forgets the interaction.

It is intentionally boring behind the scenes: one lightweight Python process,
long polling, no database, no analytics, and no queue. Clone it, add a bot
token, and keep it on your own VPS.

## Everything you actually need

| QR type | What it opens or fills in |
| --- | --- |
| 📝 Text & links | Any text, URL, invite, code, or note |
| 📶 Wi-Fi | Network name, password, and WPA/WEP/open security |
| 👤 Contact | A portable vCard with phone, email, company, website, and address |
| 📞 Phone | International formats normalized to a ready-to-dial number |
| 💬 SMS | A number and pre-filled message |
| ✉️ Email | Recipient, subject, and body |
| 📍 Location | Shared Telegram location or latitude/longitude |
| ✈️ Telegram | A profile, bot, group, or public channel link |

There are no design controls to get in the way. Every result is a standard
black-on-white PNG with sensible QR error correction and a balanced 24 px edge.

### A friendly Telegram experience

- Send any text or link for instant generation.
- Use a persistent Telegram reply keyboard for structured formats without
  adding inline controls to the conversation.
- Share a Telegram location instead of copying coordinates.
- Get automatic Russian or English UI from the Telegram language.
- Use `/cancel` at any point and `/start` to return to the menu.
- Receive a large inline image as a direct reply to the source message, keeping
  the QR code and its context together.

## Privacy by design

The shortest privacy policy is the best one:

```text
message → QR code in memory → PNG sent to Telegram → memory released
```

The bot has no user table, history, analytics, tracking, advertising SDK, or
external API beyond Telegram itself. It never writes QR contents to disk and
does not log messages, chat IDs, or user IDs. RAM keeps only a chat/user key and
the selected menu item while waiting for the next message; unfinished entries
expire after 15 minutes.

Telegram still receives messages and files as part of normal bot delivery.
For secrets that must never reach Telegram, use an offline QR generator.

## Quick start

You need a token from [@BotFather](https://t.me/BotFather) and a machine with
Docker. FFmpeg is **not** required.

### Docker Compose

```bash
git clone https://github.com/Avazbek22/qr-code-generator-tgbot.git
cd qr-code-generator-tgbot
cp .env-example .env
```

Put your token in `.env`:

```dotenv
BOT_TOKEN=123456789:replace_with_your_bot_token
```

Then start the bot:

```bash
mkdir -p data logs
sudo chown -R 10001:10001 data logs
docker compose up -d --build
docker compose ps
```

Open the bot in Telegram and send `/start`.

### One-time VPS installer with autodeploy

On Ubuntu 22.04 or 24.04, clone the repository as any user and into any
directory, then run the installer. It configures Docker Compose, starts the
bot, and enables safe updates from `origin/main`:

```bash
git clone https://github.com/Avazbek22/qr-code-generator-tgbot.git
cd qr-code-generator-tgbot
sudo bash install.sh
```

If `.env` has no token, the installer asks for it through a hidden prompt. It
then builds a candidate image, verifies the Telegram token, starts a healthy
container, and enables the deployment timer and a weekly rebuild timer.

From then on, a normal update is simply:

```bash
git push origin main
```

The VPS checks `origin/main` every two minutes and deploys a new commit once its
GitHub checks pass. A failed check, broken build, crash, or a bot that stops
receiving updates restores the previous release automatically, including during
the first ten minutes after a release. Commits that do not change the image,
such as documentation, are deployed without restarting the bot.

### Local Python development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp .env-example .env
# Add BOT_TOKEN to .env
python main.py
```

On Windows PowerShell, activate with
`.venv\Scripts\Activate.ps1`.

## Built to stay small

The production container:

- runs as the unprivileged `10001:10001` user;
- has a read-only root filesystem and drops all Linux capabilities;
- is capped at 0.5 CPU, 192 MB RAM, and 64 processes;
- writes only operational, token-redacted logs and deployment state;
- uses Docker log rotation and a tiny `/tmp` filesystem;
- exposes no port because Telegram long polling needs no reverse proxy;
- reports healthy only while Telegram answers its `getUpdates` requests.

The image contains Python, the Telegram client, Pillow, and the QR generator.
There is no browser, database server, Redis, web framework, FFmpeg, or native
QR encoder.

## Configuration

Most installations only need `BOT_TOKEN`.

| Variable | Default | Purpose |
| --- | --- | --- |
| `BOT_TOKEN` | required | Token issued by BotFather |
| `APP_NAME` | repository directory | Unique Docker/systemd name on the VPS |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` |
| `POLLING_TIMEOUT_SECONDS` | `20` | Telegram request timeout |
| `LONG_POLLING_TIMEOUT_SECONDS` | `30` | Telegram long-poll timeout |
| `HEALTH_MAX_AGE_SECONDS` | `120` | Unhealthy when `getUpdates` has not succeeded for this long |
| `TELEGRAM_API_URL` | empty | Optional self-hosted Bot API server |

The same `.env` is used locally and in Docker. It is excluded from Git and the
Docker build context. Never commit a real bot token. The installer also pins
`APP_SLUG` in `.env`, so plain `docker compose` commands find the right project.

Deployment settings — CI gate, rebuild schedule, watch window, and how many
releases to keep — live in [`deploy.conf`](deploy.conf).

## Operations

```bash
# What runs now, what it can roll back to, what deployment is waiting for
sudo bash scripts/status.sh

# Logs
docker compose logs -f --tail=100 bot

# Deploy now instead of waiting for the timer (optional)
sudo bash scripts/deploy.sh

# Try again a commit that failed before
sudo bash scripts/deploy.sh --retry

# Restore the previous release (run it again to undo)
sudo bash scripts/rollback.sh
```

See the [VPS acceptance checklist](docs/VPS_ACCEPTANCE.md) for a full production
verification.

## Fork-friendly by default

This repository is meant to be forked:

1. Fork it and rename the project if you like.
2. Update `APP_NAME` in `.env-example`.
3. Replace the README banner and repository links.
4. Add or remove formats in `app/qr.py` and `app/handlers/common.py`.
5. Keep the deployment layer unchanged unless you need different
   infrastructure.

Runtime code is deliberately separated from the tested deployment scripts, so
bot features can evolve without weakening rollback behavior.

## Quality checks

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest
shellcheck install.sh scripts/*.sh tests/shell/*.sh tests/e2e/*.sh
bash tests/shell/test-deploy.sh
ENV_FILE=.env-example APP_SLUG=qr-code-generator-tgbot \
  docker compose config --quiet
bash tests/e2e/in-docker.sh   # about ten minutes, needs Docker
```

CI runs Python tests on 3.11, 3.12, and 3.13, validates shell deployment and
rollback scenarios, builds the production image, checks its non-root,
read-only configuration, and runs the real installer and deployment scripts
against real Docker with a fake Telegram API.

## Contributing

Small, focused improvements are welcome. Please read
[CONTRIBUTING.md](CONTRIBUTING.md), avoid adding tracking or mandatory hosted
services, and never include a real bot token in an issue or log.

Security concerns should follow [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE) — use it, fork it, host it, and make it yours.

---

<div align="center">

Built for people who want a QR code—not a platform.

**telegram qr code bot · self-hosted qr generator · open source telegram bot ·
docker qr code generator · python telegram bot**

</div>
