import os
import threading
import time
from collections import OrderedDict
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

from generator import generate_post

load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"
MAX_MESSAGE_LEN = 4096

_PROCESSED_LOCK = threading.Lock()
_PROCESSED_IDS: OrderedDict = OrderedDict()
_MAX_PROCESSED = 500

HELP_TEXT = """Привет! Я генерирую посты для Telegram-канала.

Команды:
/post <тема> — написать пост
/help — эта справка

Или просто отправьте тему текстом."""


def _api(method: str, **kwargs) -> dict:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("Укажите TELEGRAM_BOT_TOKEN")

    response = requests.post(
        TELEGRAM_API.format(token=token, method=method),
        json=kwargs,
        timeout=130,
    )
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(data.get("description", "Telegram API error"))
    return data


def send_message(chat_id: int, text: str) -> None:
    for i in range(0, len(text), MAX_MESSAGE_LEN):
        _api("sendMessage", chat_id=chat_id, text=text[i : i + MAX_MESSAGE_LEN])


def _topic_from_message(text: str) -> Optional[str]:
    text = text.strip()
    if text.lower().startswith("/post"):
        return text[5:].strip() or None
    if not text or text.startswith("/"):
        return None
    return text


def _already_processed(update_id: Optional[int]) -> bool:
    if update_id is None:
        return False
    with _PROCESSED_LOCK:
        if update_id in _PROCESSED_IDS:
            return True
        _PROCESSED_IDS[update_id] = True
        while len(_PROCESSED_IDS) > _MAX_PROCESSED:
            _PROCESSED_IDS.popitem(last=False)
        return False


def handle_update(update: dict) -> None:
    if _already_processed(update.get("update_id")):
        return

    message = update.get("message") or update.get("edited_message")
    if not message or "text" not in message:
        return

    chat_id = message["chat"]["id"]
    text = message["text"].strip()

    if text in ("/start", "/help"):
        send_message(chat_id, HELP_TEXT)
        return

    topic = _topic_from_message(text)
    if not topic:
        send_message(
            chat_id,
            "Укажите тему: /post Переход из Java в ML\nили просто отправьте тему текстом.",
        )
        return

    send_message(chat_id, f"Пишу пост на тему: {topic}…")
    try:
        post = generate_post(topic)
        send_message(chat_id, post)
    except Exception as exc:
        send_message(chat_id, f"Ошибка: {exc}")


def webhook_path() -> str:
    secret = os.getenv("WEBHOOK_SECRET", "tg-webhook")
    return f"/webhook/{secret}"


def webhook_url() -> Optional[str]:
    base = os.getenv("WEBHOOK_URL") or os.getenv("RENDER_EXTERNAL_URL")
    if not base:
        return None
    return f"{base.rstrip('/')}{webhook_path()}"


def setup_webhook() -> None:
    url = webhook_url()
    if not url:
        return
    _api("setWebhook", url=url)
    print(f"Webhook: {url}")


def delete_webhook() -> None:
    _api("deleteWebhook")


def run_polling() -> None:
    delete_webhook()
    print("Бот (polling). Ctrl+C для остановки.")
    offset = 0
    while True:
        data = _api("getUpdates", offset=offset, timeout=60)
        for update in data.get("result", []):
            offset = update["update_id"] + 1
            try:
                handle_update(update)
            except Exception as exc:
                print(f"Ошибка update {update.get('update_id')}: {exc}")
        time.sleep(0.5)


if __name__ == "__main__":
    run_polling()
