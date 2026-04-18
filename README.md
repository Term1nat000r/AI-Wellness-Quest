# AI Wellness Quest

**"Худеем на здоровье"** — это фитнес-приложение нового поколения, которое решает главную проблему пользователей: отсутствие долгосрочной мотивации. В отличие от обычных приложений, мы создаем экосистему бережной поддержки, где забота о себе становится радостью, а не обязанностью.

Центральная механика строится вокруг валюты **«огоньки»**. Выполняя простые ежедневные задания (от 500 шагов до полноценной тренировки), пользователь получает огоньки и продвигается по лигам — от Бронзы до Легенды. Социальная лента показывает только пользователей того же уровня, убирая эффект «никогда не догоню». "Худеем на здоровье" не заставляет, а поддерживает, превращая одиночный путь в общее приключение.

**Технически:** Backend — Flask, frontend — HTML/CSS/JS, AI — GigaChat API.

---

## Оглавление
 
- [Демо](#демо)
- [Скриншоты](#скриншоты)
- [Архитектура](#архитектура)
- [Sequence-диаграмма](#sequence-диаграмма)
- [Структура проекта](#структура-проекта)
- [API](#api)
- [База данных](#база-данных)
- [Огоньки и лиги](#огоньки-и-лиги)
- [GigaChat интеграция](#gigachat-интеграция)
- [Запуск](#запуск)
- [Презентация](#презентация)
- 
---
## Демо

Визуал приложения можно посмотреть в файле [`index.html`](https://raw.githubusercontent.com/Term1nat000r/AI-Wellness-Quest/master/src/index.html) — откройте его в любом браузере.

---

## Скриншоты

### Меню огоньков

После нажатия на огонёк в правом верхнем углу появляется меню с:
- количеством огоньков у пользователя
- текущими заданиями на день
- количеством заморозок, оставшихся в этом месяце

![Скриншот меню огоньков](./docs/screenshot-flames-menu.png)

## Архитектура

### Уровень 1 — Контекст

<img width="2380" height="700" alt="level1_context-dark" src="https://github.com/user-attachments/assets/bc0a45aa-c0ed-403e-b230-4b7590ab8574" />

**Элементы:** Пользователь → AI Wellness Quest → GigaChat API

---

### Уровень 2 — Контейнеры

<img width="4060" height="1220" alt="level2_containers-dark" src="https://github.com/user-attachments/assets/59bea15e-74c9-4bb9-9f28-604716c33ab8" />


**Элементы:** Веб-интерфейс (HTML/CSS/JS) | Backend API (Flask) | База данных (SQLite) | AI Генератор (Python) | GigaChat API

---

### Уровень 3 — Компоненты (app.py)

<img width="1840" height="2348" alt="level3_components-dark" src="https://github.com/user-attachments/assets/9dadc011-9b43-4c90-b3ed-c02e04391964" />


**Элементы:** Лента API | Чаты API | Огоньки API | Челленджи API | Мотивация API | База данных | AI Генератор

---

### Уровень 4 — Код (gigachat.py)

<img width="2630" height="2446" alt="level4_code-dark" src="https://github.com/user-attachments/assets/2b7cdc3d-0cc1-43a0-881b-72d794b25c52" />

**Элементы:** _get_token() | _chat() | _parse_json() | generate_challenges() | generate_extra_challenge() | generate_motivation() | generate_celebration() | _fallback_* | GigaChat API

---

## Sequence-диаграмма

Показывает полный путь запроса от пользователя до ответа:

```mermaid
sequenceDiagram
    actor User as Пользователь
    participant Browser as Браузер
    participant Backend as Flask Backend
    participant DB as SQLite
    participant AI as GigaChat API

    User->>Browser: Открывает страницу
    Browser->>Backend: GET /
    Backend-->>Browser: index.html

    User->>Browser: Пишет пост
    Browser->>Backend: POST /api/posts
    Backend->>DB: Сохранить пост
    DB-->>Backend: OK
    Backend-->>Browser: {success: true}

    User->>Browser: Запрашивает челленджи
    Browser->>Backend: GET /api/challenges
    Backend->>AI: generate_challenges()
    AI-->>Backend: 5 челленджей
    Backend->>DB: Сохранить на сегодня
    Backend-->>Browser: Список заданий

    User->>Browser: Выполняет челлендж
    Browser->>Backend: POST /api/challenges/{id}/complete
    Backend->>DB: +1 огонёк
    Backend->>AI: generate_celebration()
    AI-->>Backend: Поздравление
    Backend-->>Browser: +1 🔥

## Структура проекта

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
