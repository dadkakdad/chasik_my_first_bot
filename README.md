# Telegram Time Bot

Простой Telegram бот, который отвечает на все сообщения текущим временем сервера.

## Возможности

- Отвечает на любое текстовое сообщение текущим временем сервера
- Поддерживает команду `/start` для приветствия
- Логирование всех событий и ошибок

## Требования

- Python 3.11+
- Telegram Bot Token (получить у [@BotFather](https://t.me/botfather))

## Локальная установка и запуск

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd chasik_my_first_bot
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` и добавьте токен бота:
```
BOT_TOKEN=your_bot_token_here
```

4. Запустите бота:
```bash
python bot.py
```

## Деплой на CapRover

1. Убедитесь, что CapRover CLI установлен:
```bash
npm install -g caprover
```

2. Настройте переменную окружения `BOT_TOKEN` в панели CapRover для вашего приложения

3. Задеплойте приложение:
```bash
caprover deploy
```

## Структура проекта

```
chasik_my_first_bot/
├── bot.py              # Основной код бота
├── requirements.txt    # Python зависимости
├── Dockerfile          # Docker конфигурация
├── captain-definition  # CapRover конфигурация
├── .env               # Локальные переменные окружения (не в git)
├── .gitignore         # Git ignore файл
└── README.md          # Документация
```

## Как использовать

1. Найдите вашего бота в Telegram
2. Отправьте команду `/start` для приветствия
3. Отправьте любое текстовое сообщение - бот ответит текущим временем сервера

## Технологии

- Python 3.11
- python-telegram-bot v20+ (async)
- python-dotenv
- Docker

