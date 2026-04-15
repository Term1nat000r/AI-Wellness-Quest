"""
Худеем на здоровье — Community Backend
Flask | Запуск: python3 app.py | http://localhost:5000
"""

from datetime import datetime
from flask import Flask, request, jsonify, send_file

from database import (
    get_db, init_db, user_to_dict, get_me_id, time_ago, LEAGUES,
)
from gigachat import (
    generate_challenges, generate_extra_challenge,
    generate_motivation, generate_celebration,
)

app = Flask(__name__)


# ===== Страница =====

@app.route("/")
def index():
    return send_file("index.html")


# ===== Пользователи =====

@app.route("/api/me")
def get_me():
    conn = get_db()
    r = conn.execute("SELECT * FROM users WHERE is_current_user=1").fetchone()
    conn.close()
    return jsonify(user_to_dict(r))


@app.route("/api/users")
def get_users():
    conn = get_db()
    rows = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
    conn.close()
    return jsonify([user_to_dict(r) for r in rows])


@app.route("/api/users/<int:uid>")
def get_user(uid):
    conn = get_db()
    r = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    conn.close()
    if not r:
        return jsonify({"error": "not found"}), 404
    return jsonify(user_to_dict(r))


# ===== Лента =====

@app.route("/api/feed")
def get_feed():
    tag = request.args.get("tag", "")
    conn = get_db()
    me_id = get_me_id()

    q = "SELECT p.*,u.name,u.avatar,u.avatar_color,u.flames FROM posts p JOIN users u ON p.user_id=u.id"
    params = []
    if tag and tag != "all":
        q += " WHERE p.tag=?"
        params.append(tag)
    q += " ORDER BY p.created_at DESC"

    rows = conn.execute(q, params).fetchall()
    result = []
    for r in rows:
        liked = conn.execute(
            "SELECT 1 FROM post_likes WHERE post_id=? AND user_id=?",
            (r["id"], me_id),
        ).fetchone()
        result.append({
            "id": r["id"],
            "userId": r["user_id"],
            "userName": r["name"],
            "userAvatar": r["avatar"],
            "userAvatarColor": r["avatar_color"],
            "userFlames": r["flames"],
            "text": r["text"],
            "tag": r["tag"],
            "emoji": r["emoji"],
            "likes": r["likes"],
            "comments": r["comments"],
            "liked": bool(liked),
            "time": time_ago(r["created_at"]),
        })
    conn.close()
    return jsonify(result)


@app.route("/api/posts", methods=["POST"])
def create_post():
    d = request.json
    me_id = get_me_id()
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO posts (user_id,text,tag,emoji) VALUES (?,?,?,?)",
        (me_id, d.get("text", ""), d.get("tag", ""), d.get("emoji", "")),
    )
    conn.commit()
    pid = c.lastrowid
    conn.close()
    return jsonify({"id": pid, "success": True})


@app.route("/api/posts/<int:pid>/like", methods=["POST"])
def toggle_like(pid):
    me_id = get_me_id()
    conn = get_db()
    ex = conn.execute(
        "SELECT 1 FROM post_likes WHERE post_id=? AND user_id=?", (pid, me_id)
    ).fetchone()
    if ex:
        conn.execute("DELETE FROM post_likes WHERE post_id=? AND user_id=?", (pid, me_id))
        conn.execute("UPDATE posts SET likes=likes-1 WHERE id=?", (pid,))
        liked = False
    else:
        conn.execute("INSERT INTO post_likes VALUES (?,?)", (pid, me_id))
        conn.execute("UPDATE posts SET likes=likes+1 WHERE id=?", (pid,))
        liked = True
    likes = conn.execute("SELECT likes FROM posts WHERE id=?", (pid,)).fetchone()["likes"]
    conn.commit()
    conn.close()
    return jsonify({"liked": liked, "likes": likes})


# ===== Чаты =====

@app.route("/api/chats")
def get_chats():
    me_id = get_me_id()
    conn = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    rows = conn.execute(
        "SELECT DISTINCT CASE WHEN from_user_id=? THEN to_user_id ELSE from_user_id END as pid "
        "FROM messages WHERE from_user_id=? OR to_user_id=?",
        (me_id, me_id, me_id),
    ).fetchall()
    chats = []
    for r in rows:
        p = conn.execute("SELECT * FROM users WHERE id=?", (r["pid"],)).fetchone()
        if not p:
            continue
        lm = conn.execute(
            "SELECT * FROM messages WHERE (from_user_id=? AND to_user_id=?) OR (from_user_id=? AND to_user_id=?) "
            "ORDER BY created_at DESC LIMIT 1",
            (me_id, r["pid"], r["pid"], me_id),
        ).fetchone()
        chats.append({
            "partnerId": r["pid"],
            "partnerName": p["name"],
            "partnerAvatar": p["avatar"],
            "partnerAvatarColor": p["avatar_color"],
            "partnerFlames": p["flames"],
            "partnerTodayActive": p["last_active"] == today,
            "lastMsg": lm["text"] if lm else "",
            "time": time_ago(lm["created_at"]) if lm else "",
            "unread": 0,
        })
    conn.close()
    return jsonify(chats)


@app.route("/api/chats/<int:pid>/messages")
def get_messages(pid):
    me_id = get_me_id()
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM messages WHERE (from_user_id=? AND to_user_id=?) OR (from_user_id=? AND to_user_id=?) "
        "ORDER BY created_at ASC",
        (me_id, pid, pid, me_id),
    ).fetchall()
    msgs = []
    for r in rows:
        t = ""
        if r["created_at"]:
            try:
                t = datetime.strptime(r["created_at"], "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
            except (ValueError, TypeError):
                pass
        msgs.append({
            "id": r["id"],
            "from": "me" if r["from_user_id"] == me_id else "them",
            "text": r["text"],
            "time": t,
        })
    conn.close()
    return jsonify(msgs)


@app.route("/api/chats/<int:pid>/messages", methods=["POST"])
def send_message(pid):
    me_id = get_me_id()
    text = request.json.get("text", "").strip()
    if not text:
        return jsonify({"error": "empty"}), 400
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (from_user_id,to_user_id,text) VALUES (?,?,?)",
        (me_id, pid, text),
    )
    conn.commit()
    mid = c.lastrowid
    conn.close()
    return jsonify({"id": mid, "from": "me", "text": text, "time": datetime.now().strftime("%H:%M")})


# ===== Стрики / Огоньки =====

@app.route("/api/ranking")
def get_ranking():
    conn = get_db()
    rows = conn.execute("SELECT * FROM users ORDER BY flames DESC").fetchall()
    conn.close()
    return jsonify([user_to_dict(r) for r in rows])


@app.route("/api/flames/check-penalty", methods=["POST"])
def check_penalty():
    me_id = get_me_id()
    conn = get_db()
    u = conn.execute("SELECT * FROM users WHERE id=?", (me_id,)).fetchone()
    today = datetime.now().strftime("%Y-%m-%d")
    last = u["last_active"]
    result = {"penalty": 0, "frozen": False}
    if last and last != today:
        days_missed = (datetime.now() - datetime.strptime(last, "%Y-%m-%d")).days
        if days_missed >= 2:
            if u["freezes_left"] > 0:
                conn.execute("UPDATE users SET freezes_left=freezes_left-1 WHERE id=?", (me_id,))
                result["frozen"] = True
            else:
                new_flames = max(0, u["flames"] - 3)
                conn.execute("UPDATE users SET flames=? WHERE id=?", (new_flames, me_id))
                result["penalty"] = 3
    conn.execute("UPDATE users SET last_active=? WHERE id=?", (today, me_id))
    conn.commit()
    conn.close()
    return jsonify(result)


# ===== Челленджи (GigaChat) =====

@app.route("/api/challenges")
def get_challenges():
    me_id = get_me_id()
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM daily_challenges WHERE user_id=? AND date=?", (me_id, today)
    ).fetchall()

    if len(rows) == 0:
        u = conn.execute("SELECT * FROM users WHERE id=?", (me_id,)).fetchone()
        ud = user_to_dict(u)

        picks = generate_challenges(ud["league"]["name"], ud["flames"])
        for ch in picks:
            conn.execute(
                "INSERT INTO daily_challenges (user_id,date,challenge_text,challenge_icon,challenge_cat,challenge_cat_icon,is_extra) "
                "VALUES (?,?,?,?,?,?,0)",
                (me_id, today, ch["text"], ch["icon"], ch["cat"], ch["catIcon"]),
            )

        ex = generate_extra_challenge(ud["league"]["name"], ud["flames"])
        conn.execute(
            "INSERT INTO daily_challenges (user_id,date,challenge_text,challenge_icon,challenge_cat,challenge_cat_icon,is_extra) "
            "VALUES (?,?,?,?,?,?,1)",
            (me_id, today, ex["text"], ex["icon"], ex["cat"], ex["catIcon"]),
        )
        conn.commit()
        rows = conn.execute(
            "SELECT * FROM daily_challenges WHERE user_id=? AND date=?", (me_id, today)
        ).fetchall()

    conn.close()
    return jsonify([
        {
            "id": r["id"],
            "text": r["challenge_text"],
            "icon": r["challenge_icon"],
            "cat": r["challenge_cat"],
            "catIcon": r["challenge_cat_icon"],
            "isExtra": bool(r["is_extra"]),
            "completed": bool(r["completed"]),
        }
        for r in rows
    ])


@app.route("/api/challenges/<int:cid>/complete", methods=["POST"])
def complete_challenge(cid):
    me_id = get_me_id()
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_db()
    ch = conn.execute("SELECT * FROM daily_challenges WHERE id=?", (cid,)).fetchone()
    if not ch:
        conn.close()
        return jsonify({"error": "not found"}), 404

    is_extra = bool(ch["is_extra"])
    flame_type = "extra" if is_extra else "challenge"

    already = conn.execute(
        "SELECT 1 FROM flame_log WHERE user_id=? AND date=? AND flame_type=?",
        (me_id, today, flame_type),
    ).fetchone()
    if already:
        conn.close()
        return jsonify({"error": "already done"}), 400

    conn.execute("UPDATE daily_challenges SET completed=1 WHERE id=?", (cid,))
    conn.execute(
        "INSERT INTO flame_log (user_id,date,flame_type) VALUES (?,?,?)",
        (me_id, today, flame_type),
    )
    conn.execute("UPDATE users SET flames=flames+1, last_active=? WHERE id=?", (today, me_id))
    conn.execute("UPDATE users SET record_flames=MAX(record_flames,flames) WHERE id=?", (me_id,))
    conn.commit()
    u = conn.execute("SELECT * FROM users WHERE id=?", (me_id,)).fetchone()
    conn.close()
    return jsonify({"success": True, "user": user_to_dict(u)})


@app.route("/api/flames/claim-goal", methods=["POST"])
def claim_goal_flame():
    me_id = get_me_id()
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_db()
    already = conn.execute(
        "SELECT 1 FROM flame_log WHERE user_id=? AND date=? AND flame_type='goal'",
        (me_id, today),
    ).fetchone()
    if already:
        conn.close()
        return jsonify({"error": "already claimed"}), 400
    conn.execute(
        "INSERT INTO flame_log (user_id,date,flame_type) VALUES (?,?,?)",
        (me_id, today, "goal"),
    )
    conn.execute("UPDATE users SET flames=flames+1, last_active=? WHERE id=?", (today, me_id))
    conn.execute("UPDATE users SET record_flames=MAX(record_flames,flames) WHERE id=?", (me_id,))
    conn.commit()
    u = conn.execute("SELECT * FROM users WHERE id=?", (me_id,)).fetchone()
    conn.close()
    return jsonify({"success": True, "user": user_to_dict(u)})


@app.route("/api/flames/today")
def today_flames():
    me_id = get_me_id()
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_db()
    rows = conn.execute(
        "SELECT flame_type FROM flame_log WHERE user_id=? AND date=?", (me_id, today)
    ).fetchall()
    conn.close()
    types = [r["flame_type"] for r in rows]
    return jsonify({"challenge": "challenge" in types, "goal": "goal" in types, "extra": "extra" in types})


# ===== Цели =====

@app.route("/api/goal", methods=["POST"])
def set_goal():
    me_id = get_me_id()
    d = request.json
    conn = get_db()
    conn.execute(
        "UPDATE users SET goal_steps=?, goal_water=? WHERE id=?",
        (d.get("steps", 10000), d.get("water", 2.0), me_id),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route("/api/freeze", methods=["POST"])
def use_freeze():
    me_id = get_me_id()
    conn = get_db()
    u = conn.execute("SELECT freezes_left FROM users WHERE id=?", (me_id,)).fetchone()
    if u["freezes_left"] <= 0:
        conn.close()
        return jsonify({"error": "no freezes"}), 400
    conn.execute("UPDATE users SET freezes_left=freezes_left-1 WHERE id=?", (me_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "freezesLeft": u["freezes_left"] - 1})


# ===== Мотивация (GigaChat) =====

@app.route("/api/motivation")
def get_motivation():
    h = datetime.now().hour
    conn = get_db()
    u = conn.execute("SELECT * FROM users WHERE is_current_user=1").fetchone()
    conn.close()
    return jsonify(generate_motivation(h, u["name"], u["flames"]))


@app.route("/api/celebration")
def get_celebration():
    challenge_text = request.args.get("challenge", "")
    phrase = generate_celebration(challenge_text)
    return jsonify({"phrase": phrase})


@app.route("/api/leagues")
def get_leagues():
    return jsonify(LEAGUES)


# ===== Запуск =====

if __name__ == "__main__":
    init_db()
    print("\n🚀 Сервер запущен!")
    print("📱 http://localhost:5000")
    print("⏹  Ctrl+C для остановки\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
