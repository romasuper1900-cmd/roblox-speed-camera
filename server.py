from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('speed_camera.db')
    cursor = conn.cursor()
    
    # 1. Tworzenie tabeli, jeśli nie istnieje
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            speed INTEGER NOT NULL,
            speed_limit INTEGER NOT NULL,
            location TEXT DEFAULT 'Nieokreślono',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Próba dodania kolumny location dla starszych wersji bazy
    try:
        cursor.execute("ALTER TABLE violations ADD COLUMN location TEXT DEFAULT 'Nieokreślono'")
    except sqlite3.OperationalError:
        pass  # Kolumna już istnieje

    conn.commit()
    conn.close()

# Inicjalizacja bazy danych przy starcie
init_db()

@app.route('/api/violation', methods=['POST'])
def add_violation():
    try:
        data = request.get_json(force=True)
        
        if not data or 'username' not in data or 'speed' not in data:
            return jsonify({"status": "error", "message": "Brakujące dane"}), 400

        username = str(data['username'])
        speed = int(data['speed'])
        speed_limit = int(data.get('speed_limit', 0))
        location = str(data.get('location', 'Nieznana lokalizacja'))

        # Zapis do SQLite
        conn = sqlite3.connect('speed_camera.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO violations (username, speed, speed_limit, location) VALUES (?, ?, ?, ?)",
            (username, speed, speed_limit, location)
        )
        conn.commit()
        conn.close()

        print(f"📸 [Baza Danych] Wykroczenie: {username} | {speed} km/h | Miejsce: {location}")
        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"❌ Błąd serwera: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/admin/violations', methods=['GET'])
def show_violations():
    try:
        conn = sqlite3.connect('speed_camera.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, speed, speed_limit, location, timestamp FROM violations ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()

        html = """
        <!DOCTYPE html>
        <html lang="pl">
        <head>
            <meta charset="UTF-8">
            <title>Baza Przekroczeń Prędkości</title>
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
            <h2>📸 Zafiksowane Przekroczenia Prędkości</h2>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Gracz</th>
                    <th>Prędkość</th>
                    <th>Ograniczenie</th>
                    <th>Lokalizacja</th>
                    <th>Czas (UTC)</th>
                </tr>
        """
        for row in rows:
            html += f"""
                <tr>
                    <td>{row[0]}</td>
                    <td><b>{row[1]}</b></td>
                    <td style="color: #ff6b81;">{row[2]} km/h</td>
                    <td>{row[3]} km/h 60 (+5)</td>
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
    except Exception as e:
        return f"Błąd bazy danych: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
