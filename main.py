import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "google/gemma-4-26b-a4b-it:free"
FALLBACK_MODELS = (
    "google/gemma-4-26b-a4b-it:free",
    "poolside/laguna-m.1:free",
    "z-ai/glm-4.5-air:free",
    "liquid/lfm-2.5-1.2b-instruct:free",
)


def _build_prompt(topic: str) -> str:
    return f"""Ты — автор Telegram-канала про разработку и AI.

Напиши пост на тему: {topic}

Требования:
- Длина: 150-250 слов
- Стиль: умный, но без занудства. Конкретика, без воды
- Структура: цепляющее начало, суть, вывод или вопрос в конце
- Без хэштегов
- На русском языке
"""


def _chat(api_key: str, model: str, prompt: str) -> requests.Response:
    return requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/tg-agent",
            "X-Title": "tg_agent",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=120,
    )


def generate_post(topic: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("Укажите OPENROUTER_API_KEY в файле .env")

    primary = os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL)
    models = [primary] + [m for m in FALLBACK_MODELS if m != primary]
    prompt = _build_prompt(topic)
    errors = []

    for model in models:
        response = _chat(api_key, model, prompt)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        errors.append(f"{model}: {response.status_code}")
        if response.status_code not in (429, 404, 503):
            response.raise_for_status()

    raise RuntimeError(
        "Все модели недоступны (rate limit). Повторите через минуту.\n"
        + "\n".join(errors)
    )


if __name__ == "__main__":
    topic = " ".join(sys.argv[1:]).strip() or input("Тема поста: ")
    post = generate_post(topic)
    print("\n" + "=" * 50)
    print(post)
    print("=" * 50)
