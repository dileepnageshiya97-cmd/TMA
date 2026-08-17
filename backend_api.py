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

# --- SUPER ADMIN APIs ---

@app.route('/api/admin/add-salon', methods=['POST'])
def add_salon():
    data = request.json or {}
    name = data.get('salon_name') or data.get('name')
    bot_token = data.get('bot_token')
    logo_url = data.get('logo_url') or "https://via.placeholder.com/80"
    primary_color = data.get('primary_color') or "#2563eb"
    
    if not name or not bot_token:
        return jsonify({'success': False, 'error': 'Salon Name and Bot Token are required'}), 400
        
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO salons (salon_name, bot_token) VALUES (?, ?)", (name, bot_token))
        salon_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO salon_branding (salon_id, logo_url, primary_color) VALUES (?, ?, ?)",
            (salon_id, logo_url, primary_color)
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Salon registered successfully!', 'salon_id': salon_id}), 201
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'error': 'Bot token already exists'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/metrics', methods=['GET'])
def get_metrics():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                s.salon_id, 
                s.salon_name, 
                s.bot_token, 
                s.is_active, 
                b.logo_url, 
                b.primary_color 
            FROM salons s
            LEFT JOIN salon_branding b ON s.salon_id = b.salon_id
        ''')
        salons_rows = cursor.fetchall()
        
        salons = []
        active_count = 0
        token_count = 0
        
        for row in salons_rows:
            item = dict(row)
            item['is_active'] = item['is_active'] if item['is_active'] is not None else 1
            if item['is_active']:
                active_count += 1
            if item['bot_token']:
                token_count += 1
            salons.append(item)
            
        total_salons = len(salons)
        conn.close()

        return jsonify({
            'total_salons': total_salons,
            'active_salons': active_count,
            'total_tokens': token_count,
            'salons': salons
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- CUSTOMER BOOKING APIs ---

@app.route('/api/book-appointment', methods=['POST'])
def book_appointment():
    data = request.json or {}
    salon_id = data.get('salon_id', '1')
    name = data.get('name')
    phone = data.get('phone')
    service = data.get('service', 'Haircut & Styling')
    date = data.get('date')
    time = data.get('time', '')
    amount = data.get('amount', 300)  # Frontend se received price save hoga

    if not salon_id or not name or not phone:
        return jsonify({'error': 'Salon ID, Customer Name, and Phone are required'}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO appointments (salon_id, customer_name, customer_phone, service_name, booking_date, booking_time, amount, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (salon_id, name, phone, service, date, time, amount, 'WAITING'))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Appointment booked successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- SALON OWNER DASHBOARD APIs ---

@app.route('/api/owner/bookings', methods=['GET'])
def get_owner_bookings():
    salon_id = request.args.get('salon_id', '1')
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                appointment_id AS booking_id,
                appointment_id AS token_number,
                customer_name,
                service_name,
                COALESCE(amount, 0) AS amount,
                COALESCE(status, 'WAITING') AS status
            FROM appointments
            WHERE salon_id = ?
            ORDER BY appointment_id DESC
        ''', (salon_id,))
        
        rows = cursor.fetchall()
        bookings = [dict(row) for row in rows]
        
        total_earnings = sum(b['amount'] for b in bookings if b['status'] == 'COMPLETED')
        today_customers = len(bookings)

        conn.close()
        return jsonify({
            'total_earnings': total_earnings,
            'today_customers': today_customers,
            'bookings': bookings
        }), 200
    except Exception as e:
        return jsonify({
            'total_earnings': 0,
            'today_customers': 0,
            'bookings': [],
            'error': str(e)
        }), 500


@app.route('/api/owner/update-status', methods=['POST'])
def update_booking_status():
    data = request.json or {}
    booking_id = data.get('booking_id')
    new_status = data.get('status')

    if not booking_id or not new_status:
        return jsonify({'error': 'Booking ID and status are required'}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE appointments 
            SET status = ? 
            WHERE appointment_id = ?
        ''', (new_status, booking_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Status updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)