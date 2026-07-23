from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Инициализация и авто-миграция БД
def init_db():
    conn = sqlite3.connect('speed_camera.db')
    cursor = conn.cursor()
    
    # Создаем таблицу, если ее еще нет
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            speed INTEGER NOT NULL,
            speed_limit INTEGER NOT NULL,
            location TEXT DEFAULT 'Не указано',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Добавляем колонку location, если таблица создавалась раньше без нее
    try:
        cursor.execute("ALTER TABLE violations ADD COLUMN location TEXT DEFAULT 'Не указано'")
    except sqlite3.OperationalError:
        pass # Колонка уже существует

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
    location = data.get('location', 'Неизвестное место') # Получаем место

    # Запись в SQLite
    conn = sqlite3.connect('speed_camera.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO violations (username, speed, speed_limit, location) VALUES (?, ?, ?, ?)",
        (username, speed, speed_limit, location)
    )
    conn.commit()
    conn.close()

    print(f"📸 [БД] Нарушение: {username} | {speed} км/ч | Место: {location}")
    return jsonify({"status": "success"}), 200

# HTML-таблица с добавленным столбцом "Место"
@app.route('/admin/violations', methods=['GET'])
def show_violations():
    conn = sqlite3.connect('speed_camera.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, speed, speed_limit, location, timestamp FROM violations ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

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
        <h2>📸 Zafiksowane przekróczenia prędkości</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>Gracz</th>
                <th>Prędkość</th>
                <th>Ograniczenie</th>
                <th>Miejsce</th>
                <th>Czas (UTC)</th>
            </tr>
    """
    for row in rows:
        html += f"""
            <tr>
                <td>{row[0]}</td>
                <td><b>{row[1]}</b></td>
                <td style="color: #ff6b81;">{row[2]} km/h</td>
                <td>{row[3]} km/h</td>
                <td><span style="color: #eccc68;">📍 {row[4]}</span></td>
                <td>{row[5]}</td>
            </tr>
        """
    html += """
        </table>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
