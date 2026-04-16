# AI Wellness Quest

Веб-приложение для трекинга здоровья с AI-генерацией. Backend — Flask, frontend — HTML/CSS/JS, AI — GigaChat API.

---

## Архитектура

### Уровень 1 — Контекст

![Контекст]<img width="1909" height="604" alt="image" src="https://github.com/user-attachments/assets/2d7d87fa-9ac1-44ea-8e41-3d84326babd8" />



### Уровень 2 — Контейнеры

![Контейнеры]<img width="4060" height="1329" alt="level2_containers-dark" src="https://github.com/user-attachments/assets/1ae22bd2-4821-471c-850f-acb6e283d98f" />


### Уровень 3 — Компоненты (app.py)

![Компоненты]<img width="1840" height="2458" alt="level3_components-dark" src="https://github.com/user-attachments/assets/4dece853-3455-4ac2-aad3-6cb4aaaa0267" />

### Уровень 4 — Код (gigachat.py)

![Код]<img width="2630" height="2588" alt="level4_code-dark" src="https://github.com/user-attachments/assets/cd3d4a9e-038c-4dfa-ac03-d47668cef90d" />


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
