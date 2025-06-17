# Telegram AI Friend Bot 🤖💬

Добро пожаловать в Telegram-бота-друга с ИИ!

## Возможности
- Общается как ИИ-друг (на базе OpenAI GPT)
- Кнопки для быстрого взаимодействия
- Генерация анекдотов
- Лёгкий деплой на Railway

## Установка

1. Заполни `.env` с ключами:
```
TELEGRAM_TOKEN=...
OPENAI_API_KEY=...
```

2. Установи зависимости:
```
pip install -r requirements.txt
```

3. Запусти:
```
python3 main.py
```

## Railway
Работает автоматически через `Procfile` и `railway.json`
