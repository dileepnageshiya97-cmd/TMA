import sqlite3

DB_NAME = "salon_saas.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Salons Master Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS salons (
            salon_id INTEGER PRIMARY KEY AUTOINCREMENT,
            salon_name TEXT NOT NULL,
            bot_token TEXT UNIQUE NOT NULL,
            owner_telegram_id INTEGER,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. White-Label Branding Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS salon_branding (
            branding_id INTEGER PRIMARY KEY AUTOINCREMENT,
            salon_id INTEGER UNIQUE NOT NULL,
            logo_url TEXT,
            primary_color TEXT DEFAULT '#2563eb',
            banner_text TEXT,
            FOREIGN KEY (salon_id) REFERENCES salons (salon_id)
        )
    ''')

    # 3. Appointments / Bookings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            salon_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            customer_phone TEXT,
            service_name TEXT DEFAULT 'General Haircut',
            booking_date TEXT,
            booking_time TEXT,
            status TEXT DEFAULT 'WAITING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (salon_id) REFERENCES salons (salon_id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database Multi-Tenant Tables Initialized Successfully!")

if __name__ == "__main__":
    init_db()