import sqlite3
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Ensure correct DB name used across Flask API and bots
DB_NAME = "database.db"
BASE_URL = "https://tma-backend-nkhy.onrender.com"

def get_active_salons():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT salon_id, salon_name, bot_token FROM salons WHERE is_active = 1")
        salons = cursor.fetchall()
        conn.close()
        return salons
    except Exception as e:
        print(f"⚠️ Database Error: {e}")
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    salon_id = context.bot_data["salon_id"]
    salon_name = context.bot_data["salon_name"]

    booking_url = f"{BASE_URL}/booking?salon_id={salon_id}"
    dashboard_url = f"{BASE_URL}/dashboard?salon_id={salon_id}"

    keyboard = [
        [InlineKeyboardButton("✂️ Book Token (Customer)", web_app=WebAppInfo(url=booking_url))],
        [InlineKeyboardButton("⚙️ Salon Owner Dashboard", web_app=WebAppInfo(url=dashboard_url))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Welcome to *{salon_name}*!\n\n"
        "Niche buttons par click karke Token book karein ya Live status manage karein:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def main():
    print("🚀 Multi-Bot Engine Starting...")
    running_bots = set()
    apps = []

    while True:
        salons = get_active_salons()

        if not salons:
            print("⚠️ No active salons found in Database. Pehle Master Admin se salon add karein! Retrying in 15s...")
            await asyncio.sleep(15)
            continue

        for salon_id, salon_name, bot_token in salons:
            if salon_id in running_bots:
                continue

            try:
                app = ApplicationBuilder().token(bot_token).build()
                app.bot_data["salon_id"] = salon_id
                app.bot_data["salon_name"] = salon_name
                app.add_handler(CommandHandler("start", start))

                await app.initialize()
                await app.start()
                await app.updater.start_polling()

                apps.append(app)
                running_bots.add(salon_id)
                print(f"✅ Bot Started: [{salon_name}] (ID: {salon_id})")
            except Exception as e:
                print(f"❌ Error starting bot for {salon_name}: {e}")

        # Check DB every 15 seconds for newly added salons dynamically
        await asyncio.sleep(15)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("🛑 Engine Stopped.")