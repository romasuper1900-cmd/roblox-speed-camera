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

@app.route('/admin/violations', methods=['GET'])
def show_violations():
    conn = sqlite3.connect('speed_camera.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, speed, speed_limit, timestamp FROM violations ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    # Формируем простую HTML-таблицу для браузера
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>База нарушений скорости</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 30px; background-color: #1a1a1a; color: #fff; }
            h2 { color: #ff4757; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #2f3542; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #57606f; }
            th { background-color: #70a1ff; color: #000; }
            tr:hover { background-color: #3f4858; }
        </style>
    </head>
    <body>
        <h2>📸 Зафиксированные нарушения скорости</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>Игрок</th>
                <th>Скорость</th>
                <th>Лимит</th>
                <th>Время (UTC)</th>
            </tr>
    """
    for row in rows:
        html += f"""
            <tr>
                <td>{row[0]}</td>
                <td><b>{row[1]}</b></td>
                <td style="color: #ff6b81;">{row[2]} км/ч</td>
                <td>{row[3]} км/ч</td>
                <td>{row[4]}</td>
            </tr>
        """
    html += """
        </table>
    </body>
    </html>
    """
    return html
