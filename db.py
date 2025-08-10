import sqlite3

DB_NAME = 'data/database.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        name TEXT,
                        age TEXT,
                        gender TEXT,
                        search_gender TEXT,
                        photo TEXT,
                        from_country TEXT,
                        to_country TEXT,
                        exams TEXT,
                        description TEXT,
                        language_exam TEXT,
                        ielts_score REAL,
                        toefl_score INTEGER,
                        sat_score INTEGER,
                        is_active INTEGER DEFAULT 1
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS likes (
                        user_id INTEGER,
                        liked_id INTEGER,
                        status TEXT,
                        PRIMARY KEY (user_id, liked_id)
                    )''')
    conn.commit()
    conn.close()

def save_user(data, user_id):
    required_keys = [
        'name', 'age', 'gender', 'search_gender', 'photo',
        'from_country', 'to_country', 'exams', 'description',
        'language_exam', 'ielts_score', 'toefl_score', 'sat_score'
    ]
    for key in required_keys:
        data.setdefault(key, None)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO users (
            user_id, name, age, gender, search_gender, photo,
            from_country, to_country, exams, description,
            language_exam, ielts_score, toefl_score, sat_score, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        data['name'],
        data['age'],
        data['gender'],
        data['search_gender'],
        data['photo'],
        data['from_country'],
        data['to_country'],
        data['exams'],
        data['description'],
        data['language_exam'],
        data['ielts_score'],
        data['toefl_score'],
        data['sat_score'],
        1
    ))
    conn.commit()
    conn.close()

def get_next_profile(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM users
        WHERE user_id != ?
          AND is_active = 1
          AND user_id NOT IN (
              SELECT liked_id FROM likes
              WHERE user_id = ? AND status = 'dislike'
          )
        ORDER BY RANDOM()
        LIMIT 1
    ''', (user_id, user_id))

    row = cursor.fetchone()
    conn.close()
    return row

def set_like(user_id, liked_id, status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO likes (user_id, liked_id, status) VALUES (?, ?, ?)", (user_id, liked_id, status))
    conn.commit()
    conn.close()

def is_match(user_id, liked_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM likes WHERE user_id = ? AND liked_id = ? AND status = 'like'", (liked_id, user_id))
    result = cursor.fetchone()
    conn.close()
    return bool(result)
    
def ban_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_active = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    cursor.execute("SELECT is_active FROM users WHERE user_id = ?", (user_id,))
    print(f"[BAN] Пользователь {user_id} теперь is_active = {cursor.fetchone()[0]}")
    conn.close()

def get_profiles_list(requester_id: int):
    import sqlite3
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM users
        WHERE user_id != ?
          AND is_active = 1
          AND user_id NOT IN (
              SELECT liked_id FROM likes
              WHERE user_id = ? AND status IN ('dislike', 'skipped')
          )
        ORDER BY RANDOM()
        LIMIT 50
    ''', (requester_id, requester_id))

    profiles = cursor.fetchall()
    conn.close()
    return profiles


def user_exists(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None
