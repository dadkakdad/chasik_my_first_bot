# 🚀 Setup Guide - Product Manager Bot

Пошаговая инструкция по запуску бота.

## ✅ Что уже сделано

Бот полностью реализован и готов к запуску. Вот что включено в MVP:

### Реализованные модули

1. **bot.py** - Главный файл бота
   - ✅ Telegram Bot интеграция
   - ✅ Обработчики команд: /start, /newtask, /generate, /cancel, /help
   - ✅ Обработка текстовых сообщений
   - ✅ Обработка голосовых сообщений
   - ✅ Управление сессиями
   - ✅ Генерация и отправка Markdown документов

2. **utils.py** - Утилиты и интеграции
   - ✅ OpenAI клиент с настройкой proxy
   - ✅ Whisper API для распознавания речи
   - ✅ GPT-4 для диалога
   - ✅ SessionManager для управления сессиями
   - ✅ Генератор product brief документов

3. **prompts.py** - Промпты и шаблоны
   - ✅ Системный промпт для AI-ментора
   - ✅ Промпт для генерации документов
   - ✅ Все текстовые сообщения бота

4. **requirements.txt** - Зависимости
   - ✅ python-telegram-bot 20.x
   - ✅ openai
   - ✅ aiofiles
   - ✅ python-dotenv

## 📋 Что нужно сделать для запуска

### Шаг 1: Получить API ключи

#### 1.1 Telegram Bot Token

1. Откройте [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям (имя бота, username)
4. Скопируйте полученный токен (выглядит как `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### 1.2 OpenAI API Key

1. Зайдите на [platform.openai.com](https://platform.openai.com)
2. Войдите или создайте аккаунт
3. Перейдите в API Keys (Settings → API Keys)
4. Создайте новый ключ (Create new secret key)
5. Скопируйте ключ (он показывается только один раз!)
6. **Важно:** Пополните баланс на несколько долларов для работы API

### Шаг 2: Настроить окружение

Создайте файл `.env` в корне проекта:

```env
BOT_TOKEN=ваш_telegram_bot_token
OPENAI_API_KEY=ваш_openai_api_key
OPENAI_MODEL=gpt-4-turbo
```

**Если нужен proxy для OpenAI** (например, если OpenAI недоступен в вашем регионе):

```env
BOT_TOKEN=ваш_telegram_bot_token
OPENAI_API_KEY=ваш_openai_api_key
OPENAI_MODEL=gpt-4-turbo
PROXILINE_URL=http://username:password@proxy.example.com:port
```

### Шаг 3: Установить зависимости

```bash
# Активируйте виртуальное окружение (если ещё не активировано)
source venv/bin/activate  # На macOS/Linux
# или
venv\Scripts\activate  # На Windows

# Установите зависимости
pip install -r requirements.txt
```

### Шаг 4: Запустить бота

```bash
python bot.py
```

Вы должны увидеть:
```
2025-10-23 12:00:00 - __main__ - INFO - Session manager initialized
2025-10-23 12:00:00 - __main__ - INFO - Product Manager Bot is starting...
2025-10-23 12:00:00 - __main__ - INFO - Commands: /start, /newtask, /generate, /cancel, /help
```

### Шаг 5: Протестировать бота

1. Найдите вашего бота в Telegram (по username, который вы указали в BotFather)
2. Отправьте `/start`
3. Бот должен ответить приветствием
4. Отправьте `/newtask` и опишите идею фичи
5. Отвечайте на вопросы бота
6. После диалога отправьте `/generate`
7. Получите готовый Markdown документ!

## 🧪 Проверочный список

- [ ] Python 3.11+ установлен (`python --version`)
- [ ] Виртуальное окружение создано и активировано
- [ ] Все зависимости установлены (`pip list`)
- [ ] Файл `.env` создан с корректными ключами
- [ ] Telegram Bot Token валидный
- [ ] OpenAI API Key валидный и баланс пополнен
- [ ] Proxy настроен (если нужен)
- [ ] Бот запускается без ошибок
- [ ] Бот отвечает на `/start`
- [ ] Бот может вести диалог (/newtask)
- [ ] Голосовые сообщения распознаются
- [ ] Генерация документов работает (/generate)

## 🔧 Выбор модели OpenAI

В `.env` можно указать разные модели:

| Модель | Описание | Стоимость | Рекомендация |
|--------|----------|-----------|--------------|
| `gpt-4-turbo` | Лучшее качество | ~$0.01/1K токенов | Для продакшена |
| `gpt-4o-mini` | Хорошее качество | ~$0.0001/1K токенов | Для тестов |
| `gpt-4` | Оригинальный GPT-4 | ~$0.03/1K токенов | Если нужна стабильность |

Для начала рекомендуем `gpt-4-turbo` — оптимальный баланс качества и цены.

## 🐛 Частые проблемы

### "BOT_TOKEN not found"
- Проверьте, что файл `.env` создан в корне проекта
- Убедитесь, что в `.env` нет лишних пробелов: `BOT_TOKEN=ваш_токен`

### "OPENAI_API_KEY not found"
- То же самое — проверьте `.env`
- Убедитесь, что ключ скопирован полностью

### "Error in chat completion: 401"
- OpenAI API ключ невалидный
- Создайте новый ключ на platform.openai.com

### "Error in chat completion: 429"
- Превышен лимит запросов или закончились деньги на балансе OpenAI
- Пополните баланс

### "Error in chat completion: Connection refused"
- OpenAI API недоступен в вашем регионе
- Настройте `PROXILINE_URL` в `.env`

### Бот не распознаёт голос
- Проверьте, что Whisper API доступен
- Попробуйте использовать текст вместо голоса
- Проверьте логи бота на ошибки

## 📊 Мониторинг

Бот логирует все события в консоль. Следите за логами:

```bash
python bot.py 2>&1 | tee bot.log
```

Это сохранит логи в файл `bot.log` и выведет в консоль.

## 🚀 Деплой на сервер

### Вариант 1: Запуск в фоне

```bash
nohup python bot.py > bot.log 2>&1 &
```

### Вариант 2: Systemd service (Linux)

Создайте `/etc/systemd/system/pmbot.service`:

```ini
[Unit]
Description=Product Manager Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/chasik_my_first_bot
Environment="PATH=/path/to/chasik_my_first_bot/venv/bin"
ExecStart=/path/to/chasik_my_first_bot/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Запустите:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pmbot
sudo systemctl start pmbot
sudo systemctl status pmbot
```

### Вариант 3: Docker

```bash
docker build -t pm-bot .
docker run -d --name pm-bot \
  -e BOT_TOKEN=ваш_токен \
  -e OPENAI_API_KEY=ваш_ключ \
  -e OPENAI_MODEL=gpt-4-turbo \
  --restart unless-stopped \
  pm-bot
```

## 💰 Стоимость работы бота

Примерная оценка для OpenAI API (модель gpt-4-turbo):

- **Один диалог** (10 сообщений, ~2000 токенов): ~$0.02
- **Генерация документа** (~1000 токенов): ~$0.01
- **Распознавание голоса** (1 минута): ~$0.006

**Итого:** ~$0.03 на одну полную сессию с генерацией брифа.

При 100 сессиях в месяц = ~$3/месяц

## ✨ Что дальше?

После успешного запуска:

1. **Протестируйте** на реальных идеях фич
2. **Соберите фидбек** от продакт-менеджеров
3. **Настройте** системный промпт под вашу специфику
4. **Запланируйте V2** — PostgreSQL, интеграции, аналитика

## 📞 Помощь

Если что-то не работает:

1. Проверьте логи бота
2. Убедитесь, что все ключи валидные
3. Проверьте, что все зависимости установлены
4. Создайте issue в репозитории с описанием проблемы и логами

---

**Удачи с запуском! 🚀**

