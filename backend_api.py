from flask import Flask, render_template, jsonify, request
import sqlite3

app = Flask(__name__)
DB_NAME = "salon_saas.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ----------------- PAGE ROUTES -----------------
@app.route('/super-admin')
def super_admin_page():
    return render_template('super_admin.html')

@app.route('/dashboard')
def owner_dashboard_page():
    return render_template('owner_dashboard.html')

@app.route('/booking')
def customer_booking_page():
    return render_template('customer_webapp.html')


# ----------------- 1. SUPER ADMIN APIs -----------------
@app.route('/api/admin/metrics', methods=['GET'])
def get_admin_metrics():
    conn = get_db_connection()
    total_salons = conn.execute("SELECT COUNT(*) FROM salons").fetchone()[0]
    active_salons = conn.execute("SELECT COUNT(*) FROM salons WHERE is_active = 1").fetchone()[0]
    total_tokens = conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    
    salons_list = conn.execute("""
        SELECT s.salon_id, s.salon_name, s.bot_token, s.is_active, 
               b.primary_color, b.logo_url 
        FROM salons s 
        LEFT JOIN salon_branding b ON s.salon_id = b.salon_id
    """).fetchall()
    
    conn.close()

    return jsonify({
        "total_salons": total_salons,
        "active_salons": active_salons,
        "total_tokens": total_tokens,
        "salons": [dict(r) for r in salons_list]
    })

@app.route('/api/admin/add-salon', methods=['POST'])
def add_new_salon():
    data = request.json
    salon_name = data.get('salon_name')
    bot_token = data.get('bot_token')
    logo_url = data.get('logo_url', '')
    primary_color = data.get('primary_color', '#2563eb')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO salons (salon_name, bot_token) VALUES (?, ?)", (salon_name, bot_token))
    salon_id = cursor.lastrowid
    
    cursor.execute(
        "INSERT INTO salon_branding (salon_id, logo_url, primary_color) VALUES (?, ?, ?)",
        (salon_id, logo_url, primary_color)
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "salon_id": salon_id})


# ----------------- 2. SALON OWNER APIs -----------------
@app.route('/api/owner/bookings', methods=['GET'])
def get_owner_bookings():
    salon_id = request.args.get('salon_id', 1)
    conn = get_db_connection()
    bookings = conn.execute("SELECT * FROM bookings WHERE salon_id = ? ORDER BY booking_id ASC", (salon_id,)).fetchall()
    
    # Calculate stats
    total_earnings = conn.execute("SELECT SUM(amount) FROM bookings WHERE salon_id = ? AND status = 'COMPLETED'", (salon_id,)).fetchone()[0] or 0.0
    today_customers = conn.execute("SELECT COUNT(*) FROM bookings WHERE salon_id = ?", (salon_id,)).fetchone()[0]

    conn.close()
    return jsonify({
        "bookings": [dict(row) for row in bookings],
        "total_earnings": total_earnings,
        "today_customers": today_customers
    })

@app.route('/api/owner/update-status', methods=['POST'])
def update_token_status():
    data = request.json
    booking_id = data.get('booking_id')
    new_status = data.get('status')

    conn = get_db_connection()
    conn.execute("UPDATE bookings SET status = ? WHERE booking_id = ?", (new_status, booking_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


# ----------------- 3. CUSTOMER BOOKING APIs -----------------
@app.route('/api/customer/salon-info', methods=['GET'])
def get_customer_salon_info():
    salon_id = request.args.get('salon_id', 1)
    conn = get_db_connection()
    branding = conn.execute(
        "SELECT b.*, s.salon_name FROM salon_branding b JOIN salons s ON s.salon_id = b.salon_id WHERE s.salon_id = ?", 
        (salon_id,)
    ).fetchone()
    
    current_token = conn.execute(
        "SELECT token_number FROM bookings WHERE salon_id = ? AND status = 'IN_PROGRESS' ORDER BY booking_id DESC LIMIT 1",
        (salon_id,)
    ).fetchone()
    conn.close()

    return jsonify({
        "salon_name": branding['salon_name'] if branding else "Salon",
        "logo_url": branding['logo_url'] if branding and branding['logo_url'] else "https://via.placeholder.com/80",
        "primary_color": branding['primary_color'] if branding else "#2563eb",
        "current_serving_token": current_token['token_number'] if current_token else 0
    })

@app.route('/api/customer/book-token', methods=['POST'])
def book_customer_token():
    data = request.json
    salon_id = data.get('salon_id')
    customer_name = data.get('customer_name')
    service_name = data.get('service_name', 'Haircut')
    amount = data.get('amount', 150.0)

    conn = get_db_connection()
    count = conn.execute("SELECT COUNT(*) FROM bookings WHERE salon_id = ?", (salon_id,)).fetchone()[0]
    next_token = count + 1

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO bookings (salon_id, customer_name, token_number, service_name, amount) VALUES (?, ?, ?, ?, ?)",
        (salon_id, customer_name, next_token, service_name, amount)
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "token_number": next_token})

if __name__ == '__main__':
    app.run(port=5000, debug=True)