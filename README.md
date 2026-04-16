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

---

## Демо

Визуал приложения можно посмотреть в файле [`index.html`](./index.html) — откройте его в любом браузере.

---

## Скриншоты

### Меню огоньков

После нажатия на огонёк в правом верхнем углу появляется меню с:
- количеством огоньков у пользователя
- текущими заданиями на день
- количеством заморозок, оставшихся в этом месяце

![Скриншот меню огоньков](./docs/screenshot-flames-menu.png)

> 📌 **Куда положить скриншот:** сохраните фото как `screenshot-flames-menu.png` в папку `docs/`

---

## Архитектура

### Уровень 1 — Контекст

<img width="1909" height="604" alt="image" src="https://github.com/user-attachments/assets/2d7d87fa-9ac1-44ea-8e41-3d84326babd8" />

**Элементы:** Пользователь → AI Wellness Quest → GigaChat API

---

### Уровень 2 — Контейнеры

<img width="4060" height="1329" alt="level2_containers-dark" src="https://github.com/user-attachments/assets/1ae22bd2-4821-471c-850f-acb6e283d98f" />

**Элементы:** Веб-интерфейс (HTML/CSS/JS) | Backend API (Flask) | База данных (SQLite) | AI Генератор (Python) | GigaChat API

---

### Уровень 3 — Компоненты (app.py)

<img width="1840" height="2458" alt="level3_components-dark" src="https://github.com/user-attachments/assets/4dece853-3455-4ac2-aad3-6cb4aaaa0267" />

**Элементы:** Лента API | Чаты API | Огоньки API | Челленджи API | Мотивация API | База данных | AI Генератор

---

### Уровень 4 — Код (gigachat.py)

<img width="2630" height="2588" alt="level4_code-dark" src="https://github.com/user-attachments/assets/cd3d4a9e-038c-4dfa-ac03-d47668cef90d" />

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
