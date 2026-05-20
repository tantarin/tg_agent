import os

from flask import Flask, request

from bot import handle_update, setup_webhook, webhook_path

app = Flask(__name__)


@app.route("/")
def health():
    return "tg_agent ok"


@app.route(webhook_path(), methods=["POST"])
def telegram_webhook():
    handle_update(request.get_json(force=True, silent=True) or {})
    return "", 200


setup_webhook()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
