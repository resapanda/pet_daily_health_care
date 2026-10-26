import sqlite3
import time
from datetime import datetime
import requests
import threading
from flask import Flask, request, jsonify

app = Flask(__name__)

# service is listening on this port for schedule requests
PORT = 6907
NOTIFICATIONS_DB = 'notifications.db'
# service expects consuming programs to be open and listening on this url/port
# for notifications
WEBHOOK_URL = 'http://localhost:5123/webhook'

def init_db():
    with sqlite3.connect(NOTIFICATIONS_DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Notifications (
                notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT,        -- 'PERIODIC' or 'ONE_OFF'
                title TEXT,
                message TEXT,
                notify_at REAL,
                interval_seconds INTEGER -- Seconds for periodic
            )
        """)
        # create index to look up notify_at quickly
        conn.execute("CREATE INDEX IF NOT EXISTS idx_notify_at ON Notifications(notify_at)")

def send_notification(user_id, type, title, message):
    """Sends the POST request in a separate thread."""
    try:
        requests.post(WEBHOOK_URL, json={
            "user_id": user_id,
            "type": type,
            "title": title,
            "message": message
        }, timeout=5)
    except Exception as e:
        print(f"Delivery failed : {e}")

def check_notification():
    """Background loop to check due notifications. Sends notification to webhook
    URL when notification is due."""
    while True:
        try:
            # get unix timestamp
            now = time.time()
            with sqlite3.connect(NOTIFICATIONS_DB) as conn:
                conn.row_factory = sqlite3.Row
                # fetch all due or overdue events
                due_events = conn.execute(
                    "SELECT * FROM Notifications WHERE notify_at <= ?", (now,)
                ).fetchall()

                for row in due_events:
                    if row['type'] == 'PERIODIC':
                        # Periodic: calculate next occurrence and update it
                        new_time = now + row['interval_seconds']
                        conn.execute("UPDATE Notifications SET notify_at = ? WHERE notification_id = ?", (new_time, row['notification_id']))
                    else:
                        # One-off: delete after firing
                        conn.execute("DELETE FROM Notifications WHERE notification_id = ?", (row['notification_id'],))
                    
                    conn.commit()

                    # allow us to send multiple notifications at the same time
                    # TODO: consider async runtime if perf is important?
                    threading.Thread(
                        target=send_notification, 
                        args=(row['user_id'], row['type'], row['title'], row['message'])
                    ).start()
        except Exception as e:
            print(f"Error in background loop: {e}")

        time.sleep(0.5)

@app.route('/notification', methods=['POST'])
def create_notification():
    data = request.get_json()

    # Data validation
    if not data:
        return jsonify({"ok": False, "error": "Missing JSON body"}), 400
    
    # convert notify_at to unix time stamp
    unix_time = data.get('notify_at')
    if not isinstance(unix_time, (int, float)):
        return jsonify({"error": "notify_at must be a unix timestamp"}), 400
    
    # validation to check interval is > 0 for periodic events
    n_type = data.get('type', 'ONE_OFF').upper()
    interval = int(data.get('interval_seconds', 0))

    if n_type == 'PERIODIC' and interval <= 0:
        return jsonify({"error": "PERIODIC notifications require interval_seconds > 0"}), 400
    
    # insert data into db
    try:
        conn = sqlite3.connect(NOTIFICATIONS_DB)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Notifications (user_id, type, title, message, notify_at, interval_seconds)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data['user_id'],
            n_type,
            data.get('title', ''),
            data.get('message', ''),
            unix_time,
            interval
        ))
        # get the PK(notification_id) of the row we just created
        cursor.execute("SELECT last_insert_rowid()")
        new_id = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "message": "scheduled successfully!",
            "notification_id": new_id
        }), 201
    except Exception:
        return jsonify({"error": "Internal server error"}), 500
    
@app.route('/notification/<notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    try:
        with sqlite3.connect(NOTIFICATIONS_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Notifications WHERE notification_id = ?", (notification_id,))
            if cursor.rowcount == 0:
                return jsonify({"error": "Notification not found"}), 404
            conn.commit()
        return jsonify({"message": f"Notification {notification_id} deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    init_db()
    threading.Thread(target=check_notification, daemon=True).start()
    app.run(port=PORT, debug=True, use_reloader=False)