import os
import sqlite3
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Logging setup for Render logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN")
SUPER_ADMIN_ID = os.getenv("SUPER_ADMIN_ID")
DB_NAME = "database.db"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logging.info(f"📩 /start command received from Telegram User ID: {user_id}")
    
    # Message showing exact Telegram ID of the user
    await update.message.reply_text(
        f"👑 *SaaS Master Admin Bot Live!*\n\n"
        f"👤 Aapki Telegram User ID hai: `{user_id}`\n\n"
        "Naya salon add karne ke liye command format:\n"
        "`/addsalon <SalonName> <BotToken> <LogoURL> <ThemeColor>`\n\n"
        "Example:\n"
        "`/addsalon RoyalSalon 1234567890:AAHgX... https://via.placeholder.com/80 #2563eb`",
        parse_mode="Markdown"
    )

async def add_salon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    logging.info(f"📩 /addsalon command received from ID: {user_id}")

    # Security Check: Match Telegram User ID with Render's SUPER_ADMIN_ID
    if SUPER_ADMIN_ID and user_id != str(SUPER_ADMIN_ID):
        logging.warning(f"⛔ Access Denied! Received ID: {user_id}, Expected SUPER_ADMIN_ID: {SUPER_ADMIN_ID}")
        await update.message.reply_text(
            f"❌ *Access Denied!*\n\nAapki Telegram User ID (`{user_id}`) environment variable `SUPER_ADMIN_ID` (`{SUPER_ADMIN_ID}`) se match nahi kar rahi hai.",
            parse_mode="Markdown"
        )
        return

    try:
        args = context.args
        if len(args) < 4:
            await update.message.reply_text(
                "⚠️ *Format Error!*\nDirect format:\n`/addsalon <SalonName> <BotToken> <LogoURL> <ThemeColor>`",
                parse_mode="Markdown"
            )
            return

        salon_name = args[0]
        bot_token = args[1]
        logo_url = args[2]
        theme_color = args[3]

        # Insert new salon into SQLite Database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO salons (salon_name, bot_token, logo_url, theme_color, is_active) VALUES (?, ?, ?, ?, 1)",
            (salon_name, bot_token, logo_url, theme_color)
        )
        conn.commit()
        salon_id = cursor.lastrowid
        conn.close()

        await update.message.reply_text(
            f"🎉 *Salon Onboarded Successfully!*\n\n"
            f"🆔 Salon ID: `{salon_id}`\n"
            f"💈 Salon Name: *{salon_name}*\n"
            f"🎨 Theme Color: `{theme_color}`\n\n"
            f"⚡ Multi-Bot Engine ab 15 seconds ke andar is bot ko active kar dega!",
            parse_mode="Markdown"
        )
        logging.info(f"✅ Salon Successfully Added to DB: {salon_name} (ID: {salon_id})")

    except Exception as e:
        logging.error(f"❌ Error in /addsalon execution: {e}")
        await update.message.reply_text(f"❌ Server Error: `{e}`", parse_mode="Markdown")

def main():
    if not ADMIN_BOT_TOKEN:
        logging.critical("❌ CRITICAL ERROR: ADMIN_BOT_TOKEN Environment Variable is Missing!")
        return

    logging.info("👑 SaaS Master Admin Bot Initializing...")
    app = ApplicationBuilder().token(ADMIN_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addsalon", add_salon))
    
    logging.info("🚀 Master Admin Bot is now polling for commands...")
    app.run_polling()

if __name__ == "__main__":
    main()