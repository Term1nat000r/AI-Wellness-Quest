import sqlite3
from datetime import datetime, timedelta

DB_PATH = "community.db"

LEAGUES = [
    {"name": "Бронза", "icon": "🥉", "min": 0, "max": 20, "color": "#CD7F32", "bg": "linear-gradient(135deg,#CD7F32,#E8A860)"},
    {"name": "Серебро", "icon": "🥈", "min": 21, "max": 60, "color": "#8E9AAF", "bg": "linear-gradient(135deg,#8E9AAF,#C0C7D6)"},
    {"name": "Золото", "icon": "🥇", "min": 61, "max": 120, "color": "#D4A017", "bg": "linear-gradient(135deg,#D4A017,#F5D060)"},
    {"name": "Платина", "icon": "💠", "min": 121, "max": 200, "color": "#5B8C5A", "bg": "linear-gradient(135deg,#3A7D44,#7BC67E)"},
    {"name": "Бриллиант", "icon": "💎", "min": 201, "max": 350, "color": "#2196F3", "bg": "linear-gradient(135deg,#1565C0,#42A5F5)"},
    {"name": "Мастер", "icon": "🔮", "min": 351, "max": 500, "color": "#7B1FA2", "bg": "linear-gradient(135deg,#6A1B9A,#AB47BC)"},
    {"name": "Легенда", "icon": "👑", "min": 501, "max": 99999, "color": "#FF6B35", "bg": "linear-gradient(135deg,#E65100,#FF9800)"},
]


def get_league(flames):
    for league in LEAGUES:
        if league["min"] <= flames <= league["max"]:
            return league
    return LEAGUES[0]


def get_next_league(flames):
    for i, league in enumerate(LEAGUES):
        if league["min"] <= flames <= league["max"]:
            return LEAGUES[i + 1] if i + 1 < len(LEAGUES) else None
    return None


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        avatar TEXT DEFAULT '',
        avatar_color TEXT DEFAULT '#2BC4A7',
        flames INTEGER DEFAULT 0,
        record_flames INTEGER DEFAULT 0,
        freezes_left INTEGER DEFAULT 3,
        last_active DATE,
        goal_steps INTEGER DEFAULT 10000,
        goal_water REAL DEFAULT 2.0,
        is_current_user BOOLEAN DEFAULT 0
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        tag TEXT DEFAULT '',
        emoji TEXT DEFAULT '',
        likes INTEGER DEFAULT 0,
        comments INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS post_likes (
        post_id INTEGER,
        user_id INTEGER,
        PRIMARY KEY (post_id, user_id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user_id INTEGER NOT NULL,
        to_user_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS flame_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date DATE NOT NULL,
        flame_type TEXT NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS daily_challenges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date DATE NOT NULL,
        challenge_text TEXT,
        challenge_icon TEXT,
        challenge_cat TEXT,
        challenge_cat_icon TEXT,
        is_extra BOOLEAN DEFAULT 0,
        completed BOOLEAN DEFAULT 0
    )""")
    if c.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        _seed_data(c)
    conn.commit()
    conn.close()


def _seed_data(c):
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    users = [
        ("Никита", "Н", "#2BC4A7", 20, 24, 3, today, 10000, 2.0, 1),
        ("Аня", "А", "#E91E63", 48, 52, 3, today, 8000, 2.0, 0),
        ("Дима", "Д", "#3F51B5", 10, 18, 2, yesterday, 5000, 1.5, 0),
        ("Маша", "М", "#9C27B0", 82, 82, 3, today, 10000, 2.0, 0),
        ("Серёжа", "С", "#FF9800", 5, 14, 3, today, 5000, 1.5, 0),
        ("Лена", "Л", "#00BCD4", 30, 35, 1, yesterday, 8000, 2.0, 0),
        ("Костя", "К", "#4CAF50", 115, 115, 3, today, 12000, 2.5, 0),
    ]
    c.executemany(
        "INSERT INTO users (name,avatar,avatar_color,flames,record_flames,freezes_left,last_active,goal_steps,goal_water,is_current_user) VALUES (?,?,?,?,?,?,?,?,?,?)",
        users,
    )
    posts = [
        (2, "Утренняя пробежка 5 км! Погода шикарная 🌤 Кто со мной?", "Активность", "", 12, 3),
        (6, "ПП-пицца на цветной капусте! 180 ккал 🍕", "Рецепт", "🍕", 24, 8),
        (5, "Минус 2 кг за неделю! Дневник питания помогает 💪", "Результат", "", 31, 5),
        (4, "Утренняя йога — лучшее начало дня ☀️", "Активность", "🧘‍♀️", 18, 2),
        (7, "61 огонёк! 🔥🔥🔥 Не останавливаюсь.", "Мотивация", "", 45, 12),
    ]
    for uid, text, tag, emoji, likes, comments in posts:
        c.execute(
            "INSERT INTO posts (user_id,text,tag,emoji,likes,comments) VALUES (?,?,?,?,?,?)",
            (uid, text, tag, emoji, likes, comments),
        )
    msgs = [
        (2, 1, "Привет! Пойдёшь завтра бегать?"),
        (1, 2, "Да, давай! Во сколько?"),
        (2, 1, "В 7 утра в парке?"),
        (1, 2, "Идеально, буду! 💪"),
        (4, 1, "Спасибо за рецепт! 🙏"),
        (5, 1, "Как твои успехи?"),
        (7, 1, "Погнали на марафон!"),
    ]
    c.executemany("INSERT INTO messages (from_user_id,to_user_id,text) VALUES (?,?,?)", msgs)


def user_to_dict(row):
    today = datetime.now().strftime("%Y-%m-%d")
    flames = row["flames"]
    league = get_league(flames)
    next_league = get_next_league(flames)
    return {
        "id": row["id"],
        "name": row["name"],
        "avatar": row["avatar"],
        "avatarColor": row["avatar_color"],
        "flames": flames,
        "recordFlames": row["record_flames"],
        "freezesLeft": row["freezes_left"],
        "todayActive": row["last_active"] == today,
        "isCurrentUser": bool(row["is_current_user"]),
        "goal": {"steps": row["goal_steps"], "water": row["goal_water"]},
        "league": {"name": league["name"], "icon": league["icon"], "color": league["color"], "bg": league["bg"]},
        "nextLeague": {
            "name": next_league["name"],
            "icon": next_league["icon"],
            "flamesToGo": next_league["min"] - flames,
        }
        if next_league
        else None,
    }


def get_me_id():
    conn = get_db()
    r = conn.execute("SELECT id FROM users WHERE is_current_user=1").fetchone()
    conn.close()
    return r["id"] if r else 1


def time_ago(dt_str):
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return "недавно"
    mins = int((datetime.now() - dt).total_seconds() / 60)
    if mins < 1:
        return "только что"
    if mins < 60:
        return f"{mins} мин назад"
    h = mins // 60
    return f"{h} ч назад" if h < 24 else f"{h // 24} дн назад"
