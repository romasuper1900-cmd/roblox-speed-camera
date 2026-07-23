from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Инициализация и создание таблицы в SQLite
def init_db():
    conn = sqlite3.connect('speed_camera.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            speed INTEGER NOT NULL,
            speed_limit INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/api/violation', methods=['POST'])
def add_violation():
    data = request.json
    
    if not data or 'username' not in data or 'speed' not in data:
        return jsonify({"status": "error", "message": "Неполные данные"}), 400

    username = data['username']
    speed = data['speed']
    speed_limit = data.get('speed_limit', 0)

    # Запись нарушения в базу данных
    conn = sqlite3.connect('speed_camera.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO violations (username, speed, speed_limit) VALUES (?, ?, ?)",
        (username, speed, speed_limit)
    )
    conn.commit()
    conn.close()

    print(f"📸 [БД] Зафиксировано нарушение: {username} | {speed} км/ч (Лимит: {speed_limit})")
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    init_db()
    print("🚀 Сервер запущен на http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)