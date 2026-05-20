# tg_agent

Генератор постов для Telegram-канала через [OpenRouter](https://openrouter.ai/) (бесплатные модели).

## Установка

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

В `.env` укажите ключ с https://openrouter.ai/keys

## Запуск

```bash
python main.py "Тема поста"
```
