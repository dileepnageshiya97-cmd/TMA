from flask import Flask, render_template, request, jsonify
import sqlite3
import threading
import os
import subprocess

app = Flask(__name__)
DB_NAME = "salon_saas.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Database setup
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS salons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            bot_token TEXT UNIQUE NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            salon_id INTEGER,
            customer_name TEXT,
            customer_phone TEXT,
            service_name TEXT,
            booking_date TEXT,
            booking_time TEXT,
            FOREIGN KEY (salon_id) REFERENCES salons (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- ROUTES ---

@app.route('/')
def home():
    return "Salon SaaS Backend API & Bot Engine is Live!"

@app.route('/super-admin')
def super_admin():
    return render_template('super_admin.html')

@app.route('/api/add-salon', methods=['POST'])
def add_salon():
    data = request.json
    name = data.get('name')
    bot_token = data.get('bot_token')
    
    if not name or not bot_token:
        return jsonify({'error': 'Name and Bot Token required'}), 400
        
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO salons (name, bot_token) VALUES (?, ?)", (name, bot_token))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Salon registered successfully!'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Bot token already exists'}), 400

@app.route('/booking')
def booking():
    salon_id = request.args.get('salon_id')
    return render_template('customer_webapp.html', salon_id=salon_id)

@app.route('/api/book-appointment', methods=['POST'])
def book_appointment():
    data = request.json
    salon_id = data.get('salon_id')
    name = data.get('name')
    phone = data.get('phone')
    service = data.get('service')
    date = data.get('date')
    time = data.get('time')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO appointments (salon_id, customer_name, customer_phone, service_name, booking_date, booking_time)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (salon_id, name, phone, service, date, time))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Appointment booked successfully!'}), 200

# --- BACKGROUND THREAD FOR TELEGRAM BOTS ---
def start_bot_engine():
    print("🤖 Starting Telegram Multi-Bot Engine in Background...")
    subprocess.run(["python", "multi_bot_engine.py"])

# Main process start hote hi bot engine thread mein run hoga
threading.Thread(target=start_bot_engine, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)