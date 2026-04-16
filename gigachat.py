import os
import json
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    cats_desc = ", ".join(f"{name} ({icon})" for name, icon in CATEGORIES)
    prompt = (
        f"Сгенерируй 5 челленджей для wellness-приложения, по одному из каждой категории: {cats_desc}.\n"
        f"Пользователь в лиге «{league_name}», серия огоньков: {flames}.\n"
        f"Учитывай уровень: для новичков — попроще, для опытных — посложнее.\n\n"
        f"Ответь ТОЛЬКО JSON-массивом из 5 объектов, без пояснений:\n"
        f'[{{"text": "описание задания", "icon": "эмодзи", "cat": "название категории", "catIcon": "иконка категории"}}]'
    )
    raw = _chat(
        system_prompt="Ты — тренер в wellness-приложении. Генерируешь короткие, конкретные задания на день. Отвечаешь только JSON.",
        user_prompt=prompt,
        temperature=0.9,
    )
    challenges = _parse_json(raw)
    return challenges[:5]


def generate_extra_challenge(league_name, flames):
    """Сгенерировать 1 экстра-сложный челлендж."""
    prompt = (
        f"Сгенерируй 1 экстра-сложный спортивный челлендж для wellness-приложения.\n"
        f"Пользователь в лиге «{league_name}», огоньков: {flames}.\n"
        f"Категория: «Экстра 💀», иконка категории: 🏆.\n\n"
        f"Ответь ТОЛЬКО JSON-объектом:\n"
        f'{{"text": "описание", "icon": "эмодзи", "cat": "Экстра 💀", "catIcon": "🏆"}}'
    )
    raw = _chat(
        system_prompt="Ты — тренер. Генерируешь сложные спортивные челленджи. Отвечаешь только JSON.",
        user_prompt=prompt,
        temperature=0.9,
    )
    return _parse_json(raw)


def generate_motivation(hour, user_name, flames):
    """Сгенерировать приветствие и мотивационную фразу."""
    if hour < 12:
        time_of_day = "утро"
    elif hour < 18:
        time_of_day = "день"
    else:
        time_of_day = "вечер"

    prompt = (
        f"Время суток: {time_of_day}. Пользователя зовут {user_name}, серия огоньков: {flames}.\n"
        f"Сгенерируй приветствие (2-3 слова, например «Доброе утро,») и короткую мотивационную фразу (до 50 символов, с 1 эмодзи).\n\n"
        f'Ответь ТОЛЬКО JSON: {{"greeting": "...", "phrase": "..."}}'
    )
    raw = _chat(
        system_prompt="Ты — дружелюбный wellness-коуч. Мотивируешь коротко и тепло. Отвечаешь только JSON.",
        user_prompt=prompt,
        temperature=1.0,
    )
    return _parse_json(raw)


def generate_celebration(challenge_text):
    """Сгенерировать поздравительную фразу за выполнение челленджа."""
    prompt = (
        f"Пользователь выполнил челлендж: «{challenge_text}».\n"
        f"Сгенерируй ОДНУ короткую поздравительную фразу (до 40 символов, с 1 эмодзи).\n"
        f"Ответь только текстом фразы, без кавычек."
    )
    raw = _chat(
        system_prompt="Ты — дружелюбный wellness-коуч. Хвалишь коротко и энергично.",
        user_prompt=prompt,
        temperature=1.0,
        max_tokens=100,
    )
    return raw.strip().strip('"')
