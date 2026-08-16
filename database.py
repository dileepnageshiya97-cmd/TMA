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

    # 3. Bookings & Token Records Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            salon_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            customer_phone TEXT,
            token_number INTEGER NOT NULL,
            service_name TEXT DEFAULT 'General Haircut',
            amount REAL DEFAULT 0.0,
            payment_status TEXT DEFAULT 'PAID',
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