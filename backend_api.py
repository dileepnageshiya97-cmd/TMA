from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from database import init_db

app = Flask(__name__)
DB_NAME = "salon_saas.db"

# Startup par DB initialize hoga
init_db()

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# --- ROUTES ---

@app.route('/')
def home():
    return "Salon SaaS Backend API & Bot Engine is Live!"

@app.route('/super-admin')
def super_admin():
    return render_template('super_admin.html')

@app.route('/booking')
def booking():
    salon_id = request.args.get('salon_id')
    return render_template('customer_webapp.html', salon_id=salon_id)

@app.route('/dashboard')
def dashboard():
    salon_id = request.args.get('salon_id')
    return render_template('owner_dashboard.html', salon_id=salon_id)

# --- APIs ---

@app.route('/api/add-salon', methods=['POST'])
def add_salon():
    data = request.json or {}
    name = data.get('name')
    bot_token = data.get('bot_token')
    
    if not name or not bot_token:
        return jsonify({'error': 'Salon Name and Bot Token are required'}), 400
        
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO salons (salon_name, bot_token) VALUES (?, ?)", (name, bot_token))
        salon_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO salon_branding (salon_id, logo_url, primary_color) VALUES (?, ?, ?)",
            (salon_id, "https://via.placeholder.com/80", "#2563eb")
        )
        conn.commit()
        conn.close()
        return jsonify({'message': 'Salon registered successfully!', 'salon_id': salon_id}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Bot token already exists'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/book-appointment', methods=['POST'])
def book_appointment():
    data = request.json or {}
    salon_id = data.get('salon_id')
    name = data.get('name')
    phone = data.get('phone')
    service = data.get('service', 'General Haircut')
    date = data.get('date')
    time = data.get('time')

    if not salon_id or not name:
        return jsonify({'error': 'Salon ID and Customer Name are required'}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO appointments (salon_id, customer_name, customer_phone, service_name, booking_date, booking_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (salon_id, name, phone, service, date, time))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Appointment booked successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)