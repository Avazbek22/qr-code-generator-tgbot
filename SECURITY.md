# Security Policy

## Reporting a vulnerability

Use GitHub private vulnerability reporting when it is enabled. Otherwise,
contact the repository owner through a private channel they publish. Do not
open a public issue containing a bot token, server address, exploit details, or
the contents of a private QR code.

This volunteer project does not promise a response deadline. A useful report
includes the affected version, impact, and a minimal reproduction with all
secrets removed.

## Data and trust boundaries

The bot does not persist messages or generated QR images. It does send both
through Telegram as required by the Bot API. Operators should not describe the
service as end-to-end encrypted or suitable for secrets that must not reach
Telegram.

Operational logs intentionally omit message contents, chat IDs, and user IDs.
Bot tokens are redacted by the logging formatter.

## Operator responsibilities

- Keep `.env` at mode `0600` and never commit it.
- Rotate a token immediately if it may have been exposed.
- Apply operating system and Docker security updates.
- Restrict SSH, sudo, and repository write access.
- Review dependency and deployment changes before merging them into `main`.
- Remember that anyone who can push to `main` can execute code on the VPS.
