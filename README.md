# tg_agent

Генератор постов для Telegram-канала через [OpenRouter](https://openrouter.ai/) (бесплатные модели).

## Установка

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

В `.env`:
- `OPENROUTER_API_KEY` — https://openrouter.ai/keys
- `TELEGRAM_BOT_TOKEN` — [@BotFather](https://t.me/BotFather)

## Локально (polling)

```bash
python bot.py
```

## CLI

```bash
python main.py "Тема поста"
```

## Бесплатный деплой на Render

> **GitHub Pages не подходит** — это статический хостинг. Боту нужен сервер; Render free tier + webhook.

1. Запушьте репозиторий на GitHub.
2. [render.com](https://render.com) → **New** → **Blueprint** → репозиторий `tg_agent`.
3. Вручную задайте секреты:
   - `OPENROUTER_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
4. **Deploy**. После деплоя webhook выставится сам (`RENDER_EXTERNAL_URL`).
5. Напишите боту в Telegram — первый ответ может занять ~1 мин (cold start на free).

Альтернатива: **New Web Service** → Runtime Python → Start:  
`gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120`

### Команды бота

- `/start`, `/help`
- `/post тема` или текст темы
