"""
GigaChat API — генерация контента для Wellness Quest.
Простые функции, без агентов. Fallback на захардкоженные фразы если API недоступен.

Переменные окружения:
  GIGACHAT_AUTH_KEY — ключ авторизации (base64 от client_id:client_secret)
  GIGACHAT_SCOPE   — скоуп API (по умолчанию GIGACHAT_API_PERS)
"""

import os
import json
import random
import logging
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

log = logging.getLogger(__name__)

AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

AUTH_KEY = os.getenv("GIGACHAT_AUTH_KEY", "")
SCOPE = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")

_token_cache = {"token": None, "expires_at": 0}

# ───── Авторизация ─────

def _get_token():
    """Получить OAuth-токен, кэшируя до истечения."""
    now = time.time()
    if _token_cache["token"] and now < _token_cache["expires_at"] - 60:
        return _token_cache["token"]

    resp = requests.post(
        AUTH_URL,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": f"Basic {AUTH_KEY}",
        },
        data={"scope": SCOPE},
        verify=False,
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    _token_cache["token"] = data["access_token"]
    _token_cache["expires_at"] = data.get("expires_at", now + 1800) / 1000
    return _token_cache["token"]


def _chat(system_prompt, user_prompt, temperature=0.9, max_tokens=1024):
    """Один запрос к GigaChat completions. Возвращает текст ответа."""
    token = _get_token()
    resp = requests.post(
        API_URL,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        },
        json={
            "model": "GigaChat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        verify=False,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _parse_json(text):
    """Извлечь JSON из ответа модели (может быть обёрнут в ```json ... ```)."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        text = text.rsplit("```", 1)[0]
    return json.loads(text)


# ───── Fallback-данные (если API недоступен) ─────

_FALLBACK_CHALLENGES = {
    "Упражнение": [
        {"text": "Сделай 20 приседаний", "icon": "🦵"},
        {"text": "Сделай 15 отжиманий", "icon": "💪"},
        {"text": "Планка 45 секунд", "icon": "🏋️"},
        {"text": "Потянись 10 минут", "icon": "🧘"},
    ],
    "Питание + фото": [
        {"text": "Приготовь полезный завтрак и скинь фото", "icon": "🍳"},
        {"text": "Приготовь ПП-обед и сфоткай", "icon": "🥗"},
    ],
    "Шаги": [
        {"text": "Пройди 7 000 шагов", "icon": "🚶"},
        {"text": "Пройди 10 000 шагов", "icon": "🏃"},
    ],
    "Здоровье": [
        {"text": "Помедитируй 5 минут", "icon": "🧘‍♀️"},
        {"text": "Выпей 8 стаканов воды", "icon": "💧"},
    ],
    "Социальное": [
        {"text": "Напиши другу слова поддержки", "icon": "💌"},
        {"text": "Поделись прогрессом в ленте", "icon": "📢"},
    ],
}

_FALLBACK_EXTRA = [
    {"text": "100 отжиманий за день", "icon": "💪", "cat": "Экстра 💀", "catIcon": "🏆"},
    {"text": "Табата 4 минуты", "icon": "🔥", "cat": "Экстра 💀", "catIcon": "🏆"},
    {"text": "50 берпи за день", "icon": "⚡", "cat": "Экстра 💀", "catIcon": "🏆"},
]

_FALLBACK_MOTIVATION = {
    "morning": ["Сегодня можно начать с лёгкой прогулки ☀️", "Утро — лучшее время для заботы о себе!"],
    "day": ["Маленький прогресс — это прогресс!", "Стабильность — самый сложный навык 💪"],
    "evening": ["Вечер — время заботы о себе 🌙", "День был долгим, но ты справился!"],
}

_FALLBACK_CELEBRATION = [
    "Огонь! Ты на верном пути 🔥", "Так держать! 💪", "Красавчик! Продолжай 🚀",
    "Мощно! Ты становишься сильнее ⚡", "Вот это настрой! 🙌",
]


# ───── Публичные функции ─────

CATEGORIES = [
    ("Упражнение", "💪"),
    ("Питание + фото", "📸"),
    ("Шаги", "👟"),
    ("Здоровье", "🧘"),
    ("Социальное", "🤝"),
]


def generate_challenges(league_name, flames):
    """Сгенерировать 5 дневных челленджей (по 1 из каждой категории)."""
    if not AUTH_KEY:
        return _fallback_challenges()

    cats_desc = ", ".join(f"{name} ({icon})" for name, icon in CATEGORIES)
    prompt = (
        f"Сгенерируй 5 челленджей для wellness-приложения, по одному из каждой категории: {cats_desc}.\n"
        f"Пользователь в лиге «{league_name}», серия огоньков: {flames}.\n"
        f"Учитывай уровень: для новичков — попроще, для опытных — посложнее.\n\n"
        f"Ответь ТОЛЬКО JSON-массивом из 5 объектов, без пояснений:\n"
        f'[{{"text": "описание задания", "icon": "эмодзи", "cat": "название категории", "catIcon": "иконка категории"}}]'
    )
    try:
        raw = _chat(
            system_prompt="Ты — тренер в wellness-приложении. Генерируешь короткие, конкретные задания на день. Отвечаешь только JSON.",
            user_prompt=prompt,
            temperature=0.9,
        )
        challenges = _parse_json(raw)
        if isinstance(challenges, list) and len(challenges) >= 5:
            return challenges[:5]
    except Exception as e:
        log.warning("GigaChat challenges failed, using fallback: %s", e)

    return _fallback_challenges()


def generate_extra_challenge(league_name, flames):
    """Сгенерировать 1 экстра-сложный челлендж."""
    if not AUTH_KEY:
        return random.choice(_FALLBACK_EXTRA)

    prompt = (
        f"Сгенерируй 1 экстра-сложный спортивный челлендж для wellness-приложения.\n"
        f"Пользователь в лиге «{league_name}», огоньков: {flames}.\n"
        f"Категория: «Экстра 💀», иконка категории: 🏆.\n\n"
        f"Ответь ТОЛЬКО JSON-объектом:\n"
        f'{{"text": "описание", "icon": "эмодзи", "cat": "Экстра 💀", "catIcon": "🏆"}}'
    )
    try:
        raw = _chat(
            system_prompt="Ты — тренер. Генерируешь сложные спортивные челленджи. Отвечаешь только JSON.",
            user_prompt=prompt,
            temperature=0.9,
        )
        return _parse_json(raw)
    except Exception as e:
        log.warning("GigaChat extra challenge failed: %s", e)

    return random.choice(_FALLBACK_EXTRA)


def generate_motivation(hour, user_name, flames):
    """Сгенерировать приветствие и мотивационную фразу."""
    if hour < 12:
        time_of_day, fallback_greeting = "утро", "Доброе утро,"
        fallback_pool = _FALLBACK_MOTIVATION["morning"]
    elif hour < 18:
        time_of_day, fallback_greeting = "день", "Добрый день,"
        fallback_pool = _FALLBACK_MOTIVATION["day"]
    else:
        time_of_day, fallback_greeting = "вечер", "Добрый вечер,"
        fallback_pool = _FALLBACK_MOTIVATION["evening"]

    if not AUTH_KEY:
        return {"greeting": fallback_greeting, "phrase": random.choice(fallback_pool)}

    prompt = (
        f"Время суток: {time_of_day}. Пользователя зовут {user_name}, серия огоньков: {flames}.\n"
        f"Сгенерируй приветствие (2-3 слова, например «Доброе утро,») и короткую мотивационную фразу (до 50 символов, с 1 эмодзи).\n\n"
        f'Ответь ТОЛЬКО JSON: {{"greeting": "...", "phrase": "..."}}'
    )
    try:
        raw = _chat(
            system_prompt="Ты — дружелюбный wellness-коуч. Мотивируешь коротко и тепло. Отвечаешь только JSON.",
            user_prompt=prompt,
            temperature=1.0,
        )
        return _parse_json(raw)
    except Exception as e:
        log.warning("GigaChat motivation failed: %s", e)

    return {"greeting": fallback_greeting, "phrase": random.choice(fallback_pool)}


def generate_celebration(challenge_text):
    """Сгенерировать поздравительную фразу за выполнение челленджа."""
    if not AUTH_KEY:
        return random.choice(_FALLBACK_CELEBRATION)

    prompt = (
        f"Пользователь выполнил челлендж: «{challenge_text}».\n"
        f"Сгенерируй ОДНУ короткую поздравительную фразу (до 40 символов, с 1 эмодзи).\n"
        f"Ответь только текстом фразы, без кавычек."
    )
    try:
        raw = _chat(
            system_prompt="Ты — дружелюбный wellness-коуч. Хвалишь коротко и энергично.",
            user_prompt=prompt,
            temperature=1.0,
            max_tokens=100,
        )
        return raw.strip().strip('"')
    except Exception as e:
        log.warning("GigaChat celebration failed: %s", e)

    return random.choice(_FALLBACK_CELEBRATION)


# ───── Fallback-хелпер ─────

def _fallback_challenges():
    result = []
    for cat_name, cat_icon in CATEGORIES:
        ch = random.choice(_FALLBACK_CHALLENGES[cat_name])
        result.append({"text": ch["text"], "icon": ch["icon"], "cat": cat_name, "catIcon": cat_icon})
    return result
