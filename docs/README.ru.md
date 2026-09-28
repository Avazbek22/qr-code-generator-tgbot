<div align="center">

![Telegram-бот для генерации QR-кодов](assets/qr-bot-banner.png)

# Telegram-бот для генерации QR-кодов

**Простой, приватный и полностью self-hosted бот, который превращает полезные
данные в готовые PNG QR-коды.**

[![CI](https://github.com/Avazbek22/qr-code-generator-tgbot/actions/workflows/ci.yml/badge.svg)](https://github.com/Avazbek22/qr-code-generator-tgbot/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](../LICENSE)

[English](../README.md) ·
[Быстрый запуск](#быстрый-запуск) ·
[Возможности](#всё-что-нужно-и-ничего-лишнего)

</div>

---

Иногда QR-код нужен прямо сейчас — без регистрации, кабинета, рекламы,
водяного знака и подписки. Этот бот живёт в Telegram, создаёт обычный PNG,
отправляет его и забывает взаимодействие.

Внутри всё намеренно просто: один лёгкий Python-процесс, long polling, никакой
базы данных, аналитики или очередей. Достаточно клонировать репозиторий, добавить
токен и запустить его на своём VPS.

## Всё, что нужно, и ничего лишнего

| Тип QR-кода | Что получает пользователь |
| --- | --- |
| 📝 Текст и ссылки | Любой текст, URL, приглашение, код или заметка |
| 📶 Wi-Fi | Имя сети, пароль и тип защиты WPA/WEP/open |
| 👤 Контакт | vCard с телефоном, email, компанией, сайтом и адресом |
| 📞 Телефон | Международный формат, приведённый к готовому для набора номеру |
| 💬 SMS | Номер и заранее заполненное сообщение |
| ✉️ Email | Получатель, тема и текст письма |
| 📍 Геолокация | Координаты или локация, отправленная через Telegram |
| ✈️ Telegram | Профиль, бот, группа или публичный канал |

Никаких настроек дизайна: результат всегда предсказуемый — чёрно-белый PNG с
коррекцией ошибок и сбалансированным белым краем 24 px.

Интерфейс автоматически выбирает русский или английский язык Telegram. Можно
просто отправить текст/ссылку либо выбрать нужный формат кнопкой. Команда
`/cancel` отменяет ввод, а `/start` возвращает в меню.

QR-код приходит крупным изображением в ответ на исходное сообщение, поэтому в
чате всегда видно, для каких данных он был создан. Меню отображается как
обычная Telegram-клавиатура и не засоряет чат inline-кнопками.

## Приватность без мелкого шрифта

```text
сообщение → QR в оперативной памяти → PNG в Telegram → память освобождена
```

Бот не имеет таблицы пользователей, истории, аналитики, трекеров и рекламных
SDK. Содержимое QR-кодов не записывается на диск. В логах нет сообщений, chat
ID или user ID. В RAM хранится только ключ chat/user и выбранный пункт меню;
незавершённый ввод исчезает через 15 минут.

При этом Telegram неизбежно получает сообщения и файлы в рамках обычной работы
бота. Для данных, которые нельзя передавать Telegram, используйте офлайн-
генератор.

## Быстрый запуск

Понадобятся токен от [@BotFather](https://t.me/BotFather) и Docker. FFmpeg этому
проекту не нужен.

### Docker Compose

```bash
git clone https://github.com/Avazbek22/qr-code-generator-tgbot.git
cd qr-code-generator-tgbot
cp .env-example .env
```

Добавьте токен в `.env`:

```dotenv
BOT_TOKEN=123456789:replace_with_your_bot_token
```

Запустите:

```bash
mkdir -p data logs
sudo chown -R 10001:10001 data logs
docker compose up -d --build
docker compose ps
```

Откройте бота в Telegram и отправьте `/start`.

### Установка на VPS с автодеплоем

Для Ubuntu 22.04 или 24.04 в проекте есть готовый installer. Клонировать можно
от любого пользователя и в любой каталог:

```bash
git clone https://github.com/Avazbek22/qr-code-generator-tgbot.git
cd qr-code-generator-tgbot
sudo bash install.sh
```

Если токен не заполнен, скрипт безопасно запросит его скрытым вводом. Затем он
соберёт image, проверит токен через Telegram, запустит контейнер и включит
таймер деплоя и еженедельной пересборки.

После этого для обновления достаточно:

```bash
git push origin main
```

VPS раз в две минуты проверяет `origin/main` и выкатывает новый коммит, как
только прошли его проверки в GitHub. Упавший CI, неудачная сборка, падение бота
или бот, переставший получать сообщения, автоматически возвращают прошлый релиз,
в том числе в первые десять минут после выкатки. Коммиты, которые не меняют
образ (например, документация), выкатываются без перезапуска бота.

### Локальная разработка

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp .env-example .env
# Добавьте BOT_TOKEN в .env
python main.py
```

В PowerShell окружение активируется командой
`.venv\Scripts\Activate.ps1`.

## Почему бот не нагружает VPS

- контейнер ограничен 0,5 CPU, 192 МБ RAM и 64 процессами;
- снаружи не открыт ни один порт — reverse proxy не нужен;
- нет БД, Redis, браузера, web-фреймворка и FFmpeg;
- root filesystem доступна только для чтения;
- процесс работает без root и без Linux capabilities;
- Docker-логи ротируются;
- QR создаётся через Pillow непосредственно в оперативной памяти;
- healthcheck считает бота здоровым, только пока Telegram отвечает на его
  `getUpdates`, поэтому плохие обновления безопасно откатываются.

## Настройка

Большинству установок нужен только `BOT_TOKEN`.

| Переменная | Значение | Назначение |
| --- | --- | --- |
| `BOT_TOKEN` | обязательно | Токен, полученный у BotFather |
| `APP_NAME` | каталог репозитория | Уникальное имя Docker/systemd |
| `LOG_LEVEL` | `INFO` | Уровень операционных логов |
| `POLLING_TIMEOUT_SECONDS` | `20` | Таймаут запроса к Telegram |
| `LONG_POLLING_TIMEOUT_SECONDS` | `30` | Таймаут long polling |
| `HEALTH_MAX_AGE_SECONDS` | `120` | Unhealthy, если `getUpdates` не удавался дольше |
| `TELEGRAM_API_URL` | пусто | Необязательный собственный Bot API сервер |

Файл `.env` исключён из Git и Docker build context. Никогда не коммитьте
настоящий токен. Installer закрепляет в `.env` значение `APP_SLUG`, поэтому
обычные команды `docker compose` находят нужный проект.

Настройки деплоя — ожидание CI, расписание пересборки, окно наблюдения и
количество хранимых релизов — лежат в [`deploy.conf`](../deploy.conf).

## Полезные команды

```bash
sudo bash scripts/status.sh             # что запущено, куда можно откатиться, чего ждёт деплой
docker compose logs -f --tail=100 bot   # логи
sudo bash scripts/deploy.sh             # выкатить сейчас, не дожидаясь таймера
sudo bash scripts/deploy.sh --retry     # повторить упавший коммит
sudo bash scripts/rollback.sh           # вернуть прошлый релиз (повтор — вернуть обратно)
```

Полная production-проверка находится в
[VPS acceptance checklist](VPS_ACCEPTANCE.md).

## Проект удобно форкать

1. Сделайте fork и при желании переименуйте репозиторий.
2. Измените `APP_NAME` в `.env-example`.
3. Замените баннер и ссылки в README.
4. Добавляйте форматы в `app/qr.py` и `app/handlers/common.py`.
5. Не трогайте deployment-слой, если инфраструктура остаётся прежней.

Код бота отделён от проверенных скриптов деплоя и rollback, поэтому новые
функции не должны ломать доставку обновлений.

## Проверки качества

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest
shellcheck install.sh scripts/*.sh tests/shell/*.sh tests/e2e/*.sh
bash tests/shell/test-deploy.sh
ENV_FILE=.env-example APP_SLUG=qr-code-generator-tgbot \
  docker compose config --quiet
bash tests/e2e/in-docker.sh   # около 10 минут, нужен Docker
```

CI тестирует Python 3.11–3.13, deployment и rollback, собирает production image,
проверяет non-root/read-only конфигурацию и прогоняет настоящие installer и
скрипты деплоя на настоящем Docker с поддельным Telegram API.

## Участие в проекте

Небольшие и сфокусированные улучшения приветствуются. Перед PR прочитайте
[CONTRIBUTING.md](../CONTRIBUTING.md). Не добавляйте обязательные облачные
сервисы, трекинг и настоящие токены в issues или логи.

Лицензия — [MIT](../LICENSE).
