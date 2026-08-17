import sqlite3
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

DB_NAME = "salon_saas.db"
BASE_URL = "https://tma-backend-nkhy.onrender.com"

def get_active_salons():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT salon_id, salon_name, bot_token FROM salons WHERE is_active = 1")
    salons = cursor.fetchall()
    conn.close()
    return salons

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
    salons = get_active_salons()
    if not salons:
        print("⚠️ No active salons found in Database. Pehle Master Admin se salon add karein!")
        return

    print(f"🚀 Launching Multi-Bot Engine for {len(salons)} Salons...")

    apps = []
    for salon_id, salon_name, bot_token in salons:
        try:
            app = ApplicationBuilder().token(bot_token).build()
            app.bot_data["salon_id"] = salon_id
            app.bot_data["salon_name"] = salon_name
            app.add_handler(CommandHandler("start", start))
            
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            apps.append(app)
            print(f"✅ Bot Started: [{salon_name}] (ID: {salon_id})")
        except Exception as e:
            print(f"❌ Error starting bot for {salon_name}: {e}")

    if apps:
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())