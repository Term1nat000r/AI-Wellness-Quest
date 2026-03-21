"""
Худеем на здоровье — Community Backend
Flask + SQLite | Запуск: python3 backend.py | http://localhost:5000
"""

import sqlite3, random
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)
DB_PATH = "community.db"

# ===== LEAGUES (by total flames) =====
LEAGUES = [
    {"name":"Бронза","icon":"🥉","min":0,"max":20,"color":"#CD7F32","bg":"linear-gradient(135deg,#CD7F32,#E8A860)"},
    {"name":"Серебро","icon":"🥈","min":21,"max":60,"color":"#8E9AAF","bg":"linear-gradient(135deg,#8E9AAF,#C0C7D6)"},
    {"name":"Золото","icon":"🥇","min":61,"max":120,"color":"#D4A017","bg":"linear-gradient(135deg,#D4A017,#F5D060)"},
    {"name":"Платина","icon":"💠","min":121,"max":200,"color":"#5B8C5A","bg":"linear-gradient(135deg,#3A7D44,#7BC67E)"},
    {"name":"Бриллиант","icon":"💎","min":201,"max":350,"color":"#2196F3","bg":"linear-gradient(135deg,#1565C0,#42A5F5)"},
    {"name":"Мастер","icon":"🔮","min":351,"max":500,"color":"#7B1FA2","bg":"linear-gradient(135deg,#6A1B9A,#AB47BC)"},
    {"name":"Легенда","icon":"👑","min":501,"max":99999,"color":"#FF6B35","bg":"linear-gradient(135deg,#E65100,#FF9800)"},
]

def get_league(flames):
    for l in LEAGUES:
        if l["min"] <= flames <= l["max"]: return l
    return LEAGUES[0]

def get_next_league(flames):
    for i, l in enumerate(LEAGUES):
        if l["min"] <= flames <= l["max"]:
            return LEAGUES[i+1] if i+1 < len(LEAGUES) else None
    return None

# ===== CHALLENGES =====
CH_EXERCISE = [
    {"text":"Сделай 20 приседаний","icon":"🦵","cat":"Упражнение","catIcon":"💪"},
    {"text":"Сделай 15 отжиманий (можно за день)","icon":"💪","cat":"Упражнение","catIcon":"💪"},
    {"text":"Планка 45 секунд","icon":"🏋️","cat":"Упражнение","catIcon":"💪"},
    {"text":"Потянись 10 минут","icon":"🧘","cat":"Упражнение","catIcon":"💪"},
    {"text":"Сделай 30 скручиваний на пресс","icon":"🔥","cat":"Упражнение","catIcon":"💪"},
    {"text":"10 берпи (можно с перерывами)","icon":"⚡","cat":"Упражнение","catIcon":"💪"},
    {"text":"Сделай 50 прыжков на месте","icon":"🦘","cat":"Упражнение","catIcon":"💪"},
]
CH_FOOD = [
    {"text":"Приготовь полезный завтрак и скинь фото в калькулятор","icon":"🍳","cat":"Питание + фото","catIcon":"📸"},
    {"text":"Приготовь ПП-обед и сфоткай для дневника","icon":"🥗","cat":"Питание + фото","catIcon":"📸"},
    {"text":"Сделай полезный перекус и загрузи фото","icon":"🍎","cat":"Питание + фото","catIcon":"📸"},
    {"text":"Приготовь ужин до 400 ккал и скинь фото","icon":"🍽️","cat":"Питание + фото","catIcon":"📸"},
    {"text":"Сделай смузи и сфоткай для дневника","icon":"🥤","cat":"Питание + фото","catIcon":"📸"},
]
CH_STEPS = [
    {"text":"Пройди 5 000 шагов","icon":"🚶","cat":"Шаги","catIcon":"👟"},
    {"text":"Пройди 7 000 шагов","icon":"🚶","cat":"Шаги","catIcon":"👟"},
    {"text":"Пройди 8 000 шагов","icon":"🚶‍♂️","cat":"Шаги","catIcon":"👟"},
    {"text":"Пройди 10 000 шагов","icon":"🏃","cat":"Шаги","catIcon":"👟"},
    {"text":"Пройди 12 000 шагов","icon":"🏃‍♂️","cat":"Шаги","catIcon":"👟"},
]
CH_WELLNESS = [
    {"text":"Помедитируй 5 минут","icon":"🧘‍♀️","cat":"Здоровье","catIcon":"🧘"},
    {"text":"Ложись спать до 23:00","icon":"😴","cat":"Здоровье","catIcon":"🧘"},
    {"text":"Выпей 8 стаканов воды за день","icon":"💧","cat":"Здоровье","catIcon":"🧘"},
    {"text":"Почитай книгу 15 минут","icon":"📖","cat":"Здоровье","catIcon":"🧘"},
    {"text":"Прими контрастный душ","icon":"🚿","cat":"Здоровье","catIcon":"🧘"},
]
CH_SOCIAL = [
    {"text":"Напиши другу слова поддержки","icon":"💌","cat":"Социальное","catIcon":"🤝"},
    {"text":"Поделись прогрессом в ленте","icon":"📢","cat":"Социальное","catIcon":"🤝"},
    {"text":"Поставь 5 лайков друзьям","icon":"❤️","cat":"Социальное","catIcon":"🤝"},
    {"text":"Пригласи кого-то на совместную прогулку","icon":"🤝","cat":"Социальное","catIcon":"🤝"},
]
CH_EXTRA = [
    {"text":"5 подходов по 20 приседаний с весом","icon":"🏋️‍♂️","cat":"Экстра 💀","catIcon":"🏆"},
    {"text":"Круговая тренировка: 3 раунда","icon":"⚡","cat":"Экстра 💀","catIcon":"🏆"},
    {"text":"100 отжиманий за день","icon":"💪","cat":"Экстра 💀","catIcon":"🏆"},
    {"text":"Табата 4 минуты","icon":"🔥","cat":"Экстра 💀","catIcon":"🏆"},
    {"text":"5 подходов планки по 1 минуте","icon":"🏋️","cat":"Экстра 💀","catIcon":"🏆"},
    {"text":"50 берпи за день","icon":"⚡","cat":"Экстра 💀","catIcon":"🏆"},
]

# ===== DATABASE =====
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db(); c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
        avatar TEXT DEFAULT '', avatar_color TEXT DEFAULT '#2BC4A7',
        flames INTEGER DEFAULT 0, record_flames INTEGER DEFAULT 0,
        freezes_left INTEGER DEFAULT 3, last_active DATE,
        goal_steps INTEGER DEFAULT 10000, goal_water REAL DEFAULT 2.0,
        is_current_user BOOLEAN DEFAULT 0
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
        text TEXT NOT NULL, tag TEXT DEFAULT '', emoji TEXT DEFAULT '',
        likes INTEGER DEFAULT 0, comments INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS post_likes (
        post_id INTEGER, user_id INTEGER, PRIMARY KEY (post_id, user_id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT, from_user_id INTEGER NOT NULL,
        to_user_id INTEGER NOT NULL, text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS flame_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
        date DATE NOT NULL, flame_type TEXT NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS daily_challenges (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
        date DATE NOT NULL, challenge_text TEXT, challenge_icon TEXT,
        challenge_cat TEXT, challenge_cat_icon TEXT, is_extra BOOLEAN DEFAULT 0,
        completed BOOLEAN DEFAULT 0
    )""")
    if c.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        seed_data(c)
    conn.commit(); conn.close()

def seed_data(c):
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    users = [
        ("Никита","Н","#2BC4A7",20,24,3,today,10000,2.0,1),
        ("Аня","А","#E91E63",48,52,3,today,8000,2.0,0),
        ("Дима","Д","#3F51B5",10,18,2,yesterday,5000,1.5,0),
        ("Маша","М","#9C27B0",82,82,3,today,10000,2.0,0),
        ("Серёжа","С","#FF9800",5,14,3,today,5000,1.5,0),
        ("Лена","Л","#00BCD4",30,35,1,yesterday,8000,2.0,0),
        ("Костя","К","#4CAF50",115,115,3,today,12000,2.5,0),
    ]
    c.executemany("INSERT INTO users (name,avatar,avatar_color,flames,record_flames,freezes_left,last_active,goal_steps,goal_water,is_current_user) VALUES (?,?,?,?,?,?,?,?,?,?)", users)
    posts = [
        (2,"Утренняя пробежка 5 км! Погода шикарная 🌤 Кто со мной?","Активность","",12,3),
        (6,"ПП-пицца на цветной капусте! 180 ккал 🍕","Рецепт","🍕",24,8),
        (5,"Минус 2 кг за неделю! Дневник питания помогает 💪","Результат","",31,5),
        (4,"Утренняя йога — лучшее начало дня ☀️","Активность","🧘‍♀️",18,2),
        (7,"61 огонёк! 🔥🔥🔥 Не останавливаюсь.","Мотивация","",45,12),
    ]
    for uid,text,tag,emoji,likes,comments in posts:
        c.execute("INSERT INTO posts (user_id,text,tag,emoji,likes,comments) VALUES (?,?,?,?,?,?)",(uid,text,tag,emoji,likes,comments))
    msgs = [(2,1,"Привет! Пойдёшь завтра бегать?"),(1,2,"Да, давай! Во сколько?"),(2,1,"В 7 утра в парке?"),(1,2,"Идеально, буду! 💪"),(4,1,"Спасибо за рецепт! 🙏"),(5,1,"Как твои успехи?"),(7,1,"Погнали на марафон!")]
    c.executemany("INSERT INTO messages (from_user_id,to_user_id,text) VALUES (?,?,?)", msgs)

# ===== HELPERS =====
def user_to_dict(row):
    today = datetime.now().strftime("%Y-%m-%d")
    flames = row["flames"]
    league = get_league(flames)
    next_league = get_next_league(flames)
    return {
        "id": row["id"], "name": row["name"], "avatar": row["avatar"],
        "avatarColor": row["avatar_color"], "flames": flames,
        "recordFlames": row["record_flames"], "freezesLeft": row["freezes_left"],
        "todayActive": row["last_active"] == today,
        "isCurrentUser": bool(row["is_current_user"]),
        "goal": {"steps": row["goal_steps"], "water": row["goal_water"]},
        "league": {"name": league["name"], "icon": league["icon"], "color": league["color"], "bg": league["bg"]},
        "nextLeague": {"name": next_league["name"], "icon": next_league["icon"], "flamesToGo": next_league["min"] - flames} if next_league else None,
    }

def get_me_id():
    conn = get_db()
    r = conn.execute("SELECT id FROM users WHERE is_current_user=1").fetchone()
    conn.close(); return r["id"] if r else 1

def time_ago(dt_str):
    try: dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    except: return "недавно"
    mins = int((datetime.now() - dt).total_seconds() / 60)
    if mins < 1: return "только что"
    if mins < 60: return f"{mins} мин назад"
    h = mins // 60
    return f"{h} ч назад" if h < 24 else f"{h//24} дн назад"

# ===== ROUTES =====
@app.route("/")
def index(): return send_file("index.html")

@app.route("/api/me")
def get_me():
    conn = get_db()
    r = conn.execute("SELECT * FROM users WHERE is_current_user=1").fetchone()
    conn.close(); return jsonify(user_to_dict(r))

@app.route("/api/users")
def get_users():
    conn = get_db()
    rows = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
    conn.close(); return jsonify([user_to_dict(r) for r in rows])

@app.route("/api/users/<int:uid>")
def get_user(uid):
    conn = get_db()
    r = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    conn.close()
    return jsonify(user_to_dict(r)) if r else (jsonify({"error":"not found"}), 404)

# --- Feed ---
@app.route("/api/feed")
def get_feed():
    tag = request.args.get("tag","")
    conn = get_db(); me_id = get_me_id()
    q = "SELECT p.*,u.name,u.avatar,u.avatar_color,u.flames FROM posts p JOIN users u ON p.user_id=u.id"
    if tag and tag != "all": q += f" WHERE p.tag='{tag}'"
    q += " ORDER BY p.created_at DESC"
    rows = conn.execute(q).fetchall()
    result = []
    for r in rows:
        liked = conn.execute("SELECT 1 FROM post_likes WHERE post_id=? AND user_id=?",(r["id"],me_id)).fetchone()
        result.append({"id":r["id"],"userId":r["user_id"],"userName":r["name"],"userAvatar":r["avatar"],"userAvatarColor":r["avatar_color"],"userFlames":r["flames"],"text":r["text"],"tag":r["tag"],"emoji":r["emoji"],"likes":r["likes"],"comments":r["comments"],"liked":bool(liked),"time":time_ago(r["created_at"])})
    conn.close(); return jsonify(result)

@app.route("/api/posts", methods=["POST"])
def create_post():
    d = request.json; me_id = get_me_id(); conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO posts (user_id,text,tag,emoji) VALUES (?,?,?,?)",(me_id,d.get("text",""),d.get("tag",""),d.get("emoji","")))
    conn.commit(); pid = c.lastrowid; conn.close()
    return jsonify({"id":pid,"success":True})

@app.route("/api/posts/<int:pid>/like", methods=["POST"])
def toggle_like(pid):
    me_id = get_me_id(); conn = get_db()
    ex = conn.execute("SELECT 1 FROM post_likes WHERE post_id=? AND user_id=?",(pid,me_id)).fetchone()
    if ex:
        conn.execute("DELETE FROM post_likes WHERE post_id=? AND user_id=?",(pid,me_id))
        conn.execute("UPDATE posts SET likes=likes-1 WHERE id=?",(pid,))
        liked = False
    else:
        conn.execute("INSERT INTO post_likes VALUES (?,?)",(pid,me_id))
        conn.execute("UPDATE posts SET likes=likes+1 WHERE id=?",(pid,))
        liked = True
    likes = conn.execute("SELECT likes FROM posts WHERE id=?",(pid,)).fetchone()["likes"]
    conn.commit(); conn.close()
    return jsonify({"liked":liked,"likes":likes})

# --- Chats ---
@app.route("/api/chats")
def get_chats():
    me_id = get_me_id(); conn = get_db(); today = datetime.now().strftime("%Y-%m-%d")
    rows = conn.execute("SELECT DISTINCT CASE WHEN from_user_id=? THEN to_user_id ELSE from_user_id END as pid FROM messages WHERE from_user_id=? OR to_user_id=?",(me_id,me_id,me_id)).fetchall()
    chats = []
    for r in rows:
        p = conn.execute("SELECT * FROM users WHERE id=?",(r["pid"],)).fetchone()
        if not p: continue
        lm = conn.execute("SELECT * FROM messages WHERE (from_user_id=? AND to_user_id=?) OR (from_user_id=? AND to_user_id=?) ORDER BY created_at DESC LIMIT 1",(me_id,r["pid"],r["pid"],me_id)).fetchone()
        chats.append({"partnerId":r["pid"],"partnerName":p["name"],"partnerAvatar":p["avatar"],"partnerAvatarColor":p["avatar_color"],"partnerFlames":p["flames"],"partnerTodayActive":p["last_active"]==today,"lastMsg":lm["text"] if lm else "","time":time_ago(lm["created_at"]) if lm else "","unread":0})
    conn.close(); return jsonify(chats)

@app.route("/api/chats/<int:pid>/messages")
def get_messages(pid):
    me_id = get_me_id(); conn = get_db()
    rows = conn.execute("SELECT * FROM messages WHERE (from_user_id=? AND to_user_id=?) OR (from_user_id=? AND to_user_id=?) ORDER BY created_at ASC",(me_id,pid,pid,me_id)).fetchall()
    msgs = [{"id":r["id"],"from":"me" if r["from_user_id"]==me_id else "them","text":r["text"],"time":datetime.strptime(r["created_at"],"%Y-%m-%d %H:%M:%S").strftime("%H:%M") if r["created_at"] else ""} for r in rows]
    conn.close(); return jsonify(msgs)

@app.route("/api/chats/<int:pid>/messages", methods=["POST"])
def send_message(pid):
    me_id = get_me_id(); text = request.json.get("text","").strip()
    if not text: return jsonify({"error":"empty"}),400
    conn = get_db(); c = conn.cursor()
    c.execute("INSERT INTO messages (from_user_id,to_user_id,text) VALUES (?,?,?)",(me_id,pid,text))
    conn.commit(); mid = c.lastrowid; conn.close()
    return jsonify({"id":mid,"from":"me","text":text,"time":datetime.now().strftime("%H:%M")})

# --- Streaks / Flames ---
@app.route("/api/ranking")
def get_ranking():
    conn = get_db()
    rows = conn.execute("SELECT * FROM users ORDER BY flames DESC").fetchall()
    conn.close(); return jsonify([user_to_dict(r) for r in rows])

@app.route("/api/flames/check-penalty", methods=["POST"])
def check_penalty():
    """Check if user missed 2+ days and apply -3 flames penalty (unless frozen)"""
    me_id = get_me_id(); conn = get_db()
    u = conn.execute("SELECT * FROM users WHERE id=?",(me_id,)).fetchone()
    today = datetime.now().strftime("%Y-%m-%d")
    last = u["last_active"]
    result = {"penalty":0,"frozen":False}
    if last and last != today:
        days_missed = (datetime.now() - datetime.strptime(last,"%Y-%m-%d")).days
        if days_missed >= 2:
            if u["freezes_left"] > 0:
                conn.execute("UPDATE users SET freezes_left=freezes_left-1 WHERE id=?",(me_id,))
                result["frozen"] = True
            else:
                new_flames = max(0, u["flames"] - 3)
                conn.execute("UPDATE users SET flames=? WHERE id=?",(new_flames,me_id))
                result["penalty"] = 3
    conn.execute("UPDATE users SET last_active=? WHERE id=?",(today,me_id))
    conn.commit(); conn.close()
    return jsonify(result)

# --- Challenges ---
@app.route("/api/challenges")
def get_challenges():
    """Get today's 5 challenges + optional extra"""
    me_id = get_me_id(); today = datetime.now().strftime("%Y-%m-%d"); conn = get_db()
    rows = conn.execute("SELECT * FROM daily_challenges WHERE user_id=? AND date=?",(me_id,today)).fetchall()
    if len(rows) == 0:
        picks = [random.choice(CH_EXERCISE),random.choice(CH_FOOD),random.choice(CH_STEPS),random.choice(CH_WELLNESS),random.choice(CH_SOCIAL)]
        for ch in picks:
            conn.execute("INSERT INTO daily_challenges (user_id,date,challenge_text,challenge_icon,challenge_cat,challenge_cat_icon,is_extra) VALUES (?,?,?,?,?,?,0)",(me_id,today,ch["text"],ch["icon"],ch["cat"],ch["catIcon"]))
        # Extra (always for demo; in prod: random.random() < 0.15)
        ex = random.choice(CH_EXTRA)
        conn.execute("INSERT INTO daily_challenges (user_id,date,challenge_text,challenge_icon,challenge_cat,challenge_cat_icon,is_extra) VALUES (?,?,?,?,?,?,1)",(me_id,today,ex["text"],ex["icon"],ex["cat"],ex["catIcon"]))
        conn.commit()
        rows = conn.execute("SELECT * FROM daily_challenges WHERE user_id=? AND date=?",(me_id,today)).fetchall()
    conn.close()
    return jsonify([{"id":r["id"],"text":r["challenge_text"],"icon":r["challenge_icon"],"cat":r["challenge_cat"],"catIcon":r["challenge_cat_icon"],"isExtra":bool(r["is_extra"]),"completed":bool(r["completed"])} for r in rows])

@app.route("/api/challenges/<int:cid>/complete", methods=["POST"])
def complete_challenge(cid):
    me_id = get_me_id(); today = datetime.now().strftime("%Y-%m-%d"); conn = get_db()
    ch = conn.execute("SELECT * FROM daily_challenges WHERE id=?",(cid,)).fetchone()
    if not ch: conn.close(); return jsonify({"error":"not found"}),404
    is_extra = bool(ch["is_extra"])
    # For regular challenges, check if already got a regular flame today
    if not is_extra:
        already = conn.execute("SELECT 1 FROM flame_log WHERE user_id=? AND date=? AND flame_type='challenge'",(me_id,today)).fetchone()
        if already: conn.close(); return jsonify({"error":"already done"}),400
    else:
        already = conn.execute("SELECT 1 FROM flame_log WHERE user_id=? AND date=? AND flame_type='extra'",(me_id,today)).fetchone()
        if already: conn.close(); return jsonify({"error":"already done"}),400
    conn.execute("UPDATE daily_challenges SET completed=1 WHERE id=?",(cid,))
    flame_type = "extra" if is_extra else "challenge"
    conn.execute("INSERT INTO flame_log (user_id,date,flame_type) VALUES (?,?,?)",(me_id,today,flame_type))
    conn.execute("UPDATE users SET flames=flames+1, last_active=? WHERE id=?",(today,me_id))
    conn.execute("UPDATE users SET record_flames=MAX(record_flames,flames) WHERE id=?",(me_id,))
    conn.commit()
    u = conn.execute("SELECT * FROM users WHERE id=?",(me_id,)).fetchone()
    conn.close()
    return jsonify({"success":True,"user":user_to_dict(u)})

@app.route("/api/flames/claim-goal", methods=["POST"])
def claim_goal_flame():
    """Claim flame for completing daily goal"""
    me_id = get_me_id(); today = datetime.now().strftime("%Y-%m-%d"); conn = get_db()
    already = conn.execute("SELECT 1 FROM flame_log WHERE user_id=? AND date=? AND flame_type='goal'",(me_id,today)).fetchone()
    if already: conn.close(); return jsonify({"error":"already claimed"}),400
    conn.execute("INSERT INTO flame_log (user_id,date,flame_type) VALUES (?,?,?)",(me_id,today,"goal"))
    conn.execute("UPDATE users SET flames=flames+1, last_active=? WHERE id=?",(today,me_id))
    conn.execute("UPDATE users SET record_flames=MAX(record_flames,flames) WHERE id=?",(me_id,))
    conn.commit()
    u = conn.execute("SELECT * FROM users WHERE id=?",(me_id,)).fetchone()
    conn.close()
    return jsonify({"success":True,"user":user_to_dict(u)})

@app.route("/api/flames/today")
def today_flames():
    """Get what flames were earned today"""
    me_id = get_me_id(); today = datetime.now().strftime("%Y-%m-%d"); conn = get_db()
    rows = conn.execute("SELECT flame_type FROM flame_log WHERE user_id=? AND date=?",(me_id,today)).fetchall()
    conn.close()
    types = [r["flame_type"] for r in rows]
    return jsonify({"challenge":"challenge" in types, "goal":"goal" in types, "extra":"extra" in types})

# --- Goals ---
@app.route("/api/goal", methods=["POST"])
def set_goal():
    me_id = get_me_id(); d = request.json; conn = get_db()
    conn.execute("UPDATE users SET goal_steps=?, goal_water=? WHERE id=?",(d.get("steps",10000),d.get("water",2.0),me_id))
    conn.commit(); conn.close()
    return jsonify({"success":True})

# --- Freeze ---
@app.route("/api/freeze", methods=["POST"])
def use_freeze():
    me_id = get_me_id(); conn = get_db()
    u = conn.execute("SELECT freezes_left FROM users WHERE id=?",(me_id,)).fetchone()
    if u["freezes_left"] <= 0: conn.close(); return jsonify({"error":"no freezes"}),400
    conn.execute("UPDATE users SET freezes_left=freezes_left-1 WHERE id=?",(me_id,))
    conn.commit(); conn.close()
    return jsonify({"success":True,"freezesLeft":u["freezes_left"]-1})

# --- Motivation ---
@app.route("/api/motivation")
def get_motivation():
    h = datetime.now().hour
    if h < 12:
        phrases = ["Сегодня можно начать с лёгкой прогулки ☀️","Утро — лучшее время для заботы о себе!","Новый день — новые огоньки 🔥","Каждое утро — шанс стать лучше 🌅"]
    elif h >= 18:
        phrases = ["Вечер — время заботы о себе 🌙","5 минут растяжки перед сном — чудо","День был долгим, но ты справился!"]
    else:
        phrases = ["Стабильность — самый сложный навык 💪","Маленький прогресс — это прогресс!","Ты круче 90% людей 🚀","Черепаха тоже финишировала! 🐢"]
    greeting = "Доброе утро," if h<12 else ("Добрый день," if h<18 else "Добрый вечер,")
    return jsonify({"greeting":greeting,"phrase":random.choice(phrases)})

@app.route("/api/leagues")
def get_leagues(): return jsonify(LEAGUES)

@app.route("/api/celebration")
def get_celebration():
    """Random celebration phrase for flame completion"""
    phrases = [
        "Огонь! Ты на верном пути 🔥","Так держать! 💪","Красавчик! Продолжай 🚀",
        "Мощно! Ты становишься сильнее ⚡","Серия растёт! 🏆","Вот это настрой! 🙌",
        "Ты лучше, чем вчера ✨","Прогресс налицо! 📈","Ближе к цели 🎯",
        "Это было легко, правда? 😎","Ты в огне! 🔥","Скоро новая лига! 🥇",
    ]
    return jsonify({"phrase": random.choice(phrases)})

# ===== START =====
if __name__ == "__main__":
    init_db()
    print("\n🚀 Сервер запущен!")
    print("📱 http://localhost:5000")
    print("⏹  Ctrl+C для остановки\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
