import os
import threading

from flask import Flask, request

from bot import handle_update, setup_webhook, webhook_path

app = Flask(__name__)


@app.route("/")
def health():
    return "tg_agent ok"


@app.route(webhook_path(), methods=["POST"])
def telegram_webhook():
    update = request.get_json(force=True, silent=True) or {}
    # Сразу 200 — иначе Telegram повторяет webhook, пока идёт генерация (минуты).
    threading.Thread(target=handle_update, args=(update,), daemon=True).start()
    return "", 200


setup_webhook()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
