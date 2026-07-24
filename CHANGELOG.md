# Changelog

All notable changes to QR Code Generator Telegram Bot are documented here.

## [Unreleased]

### Fixed

- Smoke tests no longer use the unsupported Docker Compose `run --no-build`
  flag, improving compatibility with older Compose v2 installations.

### Added

- Russian and English user interface selected from Telegram language.
- One-tap generation for text, URLs, Wi-Fi, vCard contacts, phone calls, SMS,
  email, geolocation, and Telegram links.
- In-memory PNG generation without message history, database, or user tracking.
- Scanner-friendly QR defaults and uncompressed document delivery.
- Automatic Telegram command menu and cancellable input flows.
- Lightweight Docker resource limits: 0.5 CPU, 192 MB RAM, and 64 processes.
- English and Russian project guides with a dedicated README banner.
- Unit tests for every QR payload type and PNG output.

### Retained from the deployment template

- Hardened non-root, read-only Docker container with heartbeat healthcheck.
- Idempotent Ubuntu installer and project-specific systemd autodeploy timer.
- Candidate smoke tests, fast-forward updates, failed-release suppression, and
  automatic or manual rollback.
- Python, shell, Compose, and Docker CI coverage.

## [1.0.0] - 2026-07-25

First complete self-hosted QR bot release.
