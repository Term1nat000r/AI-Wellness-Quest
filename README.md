# AI Wellness Quest

Веб-приложение для трекинга здоровья с AI-генерацией. Backend — Flask, frontend — HTML/CSS/JS, AI — GigaChat API.

---

## Архитектура

### Уровень 1 — Контекст

![Контекст](./docs/level1-context.png)

### Уровень 2 — Контейнеры

![Контейнеры](./docs/level2-containers.png)

### Уровень 3 — Компоненты (app.py)

![Компоненты](./docs/level3-components.png)

### Уровень 4 — Код (gigachat.py)

![Код](./docs/level4-code.png)

---

## API

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/me` | Текущий пользователь |
| GET | `/api/users` | Все пользователи |
| GET | `/api/feed` | Лента постов |
| POST | `/api/posts` | Создать пост |
| POST | `/api/posts/{id}/like` | Лайк |
| GET | `/api/chats` | Список диалогов |
| GET | `/api/chats/{id}/messages` | История |
| POST | `/api/chats/{id}/messages` | Отправить |
| GET | `/api/ranking` | Рейтинг |
| GET | `/api/challenges` | Челленджи дня |
| POST | `/api/challenges/{id}/complete` | Выполнить |
| POST | `/api/flames/claim-goal` | Забрать огонёк |
| POST | `/api/freeze` | Заморозка |
| GET | `/api/motivation` | Мотивация |

---

## База данных

### Таблицы

| Таблица | Поля |
|---------|------|
| users | id, name, avatar, flames, record_flames, freezes_left, last_active |
| posts | id, user_id, text, tag, likes, comments, created_at |
| messages | id, from_user_id, to_user_id, text, created_at |
| daily_challenges | id, user_id, date, challenge_text, completed, is_extra |
| flame_log | id, user_id, date, flame_type |

---

## Огоньки и лиги

| Диапазон | Лига |
|----------|------|
| 0-20 | Бронза 🥉 |
| 21-60 | Серебро 🥈 |
| 61-120 | Золото 🥇 |
| 121-200 | Платина 💠 |
| 201-350 | Бриллиант 💎 |
| 351-500 | Мастер 🔮 |
| 501+ | Легенда 👑 |

| Действие | Огоньки |
|----------|---------|
| Выполнить челлендж | +1 |
| Выполнить экстра-челлендж | +2 |
| Выполнить цели | +1 |
| Пропуск 1 дня | -1 |
| Пропуск 2+ дней | -3 |

---

## GigaChat интеграция

### Эндпоинты

| Назначение | URL |
|------------|-----|
| Авторизация | `https://ngw.devices.sberbank.ru:9443/api/v2/oauth` |
| Генерация | `https://gigachat.devices.sberbank.ru/api/v1/chat/completions` |

### Функции gigachat.py

| Функция | Назначение |
|---------|------------|
| `_get_token()` | OAuth, кэш токена |
| `_chat()` | Базовый запрос |
| `_parse_json()` | Извлечение JSON |
| `generate_challenges()` | 5 челленджей |
| `generate_extra_challenge()` | Экстра-челлендж |
| `generate_motivation()` | Приветствие + фраза |
| `generate_celebration()` | Поздравление |
| `_fallback_*` | Запасные данные |

---

## Запуск

```bash
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate
pip install flask requests
echo "GIGACHAT_AUTH_KEY=your_key" > .env
python app.py
