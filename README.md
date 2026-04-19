# AI Wellness Quest

**"Худеем на здоровье"** — это фитнес-приложение нового поколения, которое решает главную проблему пользователей: отсутствие долгосрочной мотивации. В отличие от обычных приложений, мы создаем экосистему бережной поддержки, где забота о себе становится радостью, а не обязанностью.

Центральная механика строится вокруг валюты **«огоньки»**. Выполняя простые ежедневные задания (от 500 шагов до полноценной тренировки), пользователь получает огоньки и продвигается по лигам — от Бронзы до Легенды. Социальная лента показывает только пользователей того же уровня, убирая эффект «никогда не догоню». "Худеем на здоровье" не заставляет, а поддерживает, превращая одиночный путь в общее приключение.

**Технически:** Backend — Flask, frontend — HTML/CSS/JS, AI — GigaChat API.

---

## Стек технологий

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![GigaChat](https://img.shields.io/badge/GigaChat-21A038?style=flat-square&logo=sberbank&logoColor=white)

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

---

## Демо

Визуал приложения можно посмотреть [здесь](https://Term1nat000r.github.io/AI-Wellness-Quest/) — откройте в любом браузере.

---

## Скриншоты

### Меню огоньков

После нажатия на огонёк в правом верхнем углу появляется меню с:
- количеством огоньков у пользователя
- текущими заданиями на день
- количеством заморозок, оставшихся в этом месяце

![Скриншот меню огоньков](./docs/screenshot-flames-menu.png)

<!-- TODO: добавить скриншоты ленты, рейтинга, чатов -->

---

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
```

---

## Структура проекта

```
AI-Wellness-Quest/
├── app.py                  # Flask backend: роуты, API, работа с БД
├── gigachat.py             # Обёртка над GigaChat API: OAuth, генерация
├── database.db             # SQLite база (создаётся при первом запуске)
├── requirements.txt        # Python-зависимости
├── .env                    # Переменные окружения (GIGACHAT_AUTH_KEY)
│
├── templates/              # HTML-шаблоны
│   └── index.html
│
├── static/                 # Frontend-ассеты
│   ├── css/
│   ├── js/
│   └── img/
│
└── docs/                   # Документация и скриншоты
    └── screenshot-flames-menu.png
```

> ⚠️ Приведена ориентировочная структура. Уточни по реальному дереву репозитория.

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

### Требования

- Python 3.10+
- Ключ авторизации GigaChat API ([получить здесь](https://developers.sber.ru/portal/products/gigachat-api))

### Установка

**1. Клонировать репозиторий**

```bash
git clone https://github.com/Term1nat000r/AI-Wellness-Quest.git
cd AI-Wellness-Quest
```

**2. Создать виртуальное окружение**

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Установить зависимости**

```bash
pip install -r requirements.txt
```

Если `requirements.txt` ещё нет:

```bash
pip install flask requests python-dotenv
```

**4. Настроить переменные окружения**

Создай файл `.env` в корне проекта:

```env
GIGACHAT_AUTH_KEY=your_auth_key_here
```

**5. Запустить приложение**

```bash
python app.py
```

Приложение будет доступно по адресу `http://localhost:5000`.
