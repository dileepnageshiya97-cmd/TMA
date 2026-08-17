import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

ADMIN_BOT_TOKEN = "YOUR_MASTER_ADMIN_BOT_TOKEN_HERE"  # Apni token yahan daalein
SUPER_ADMIN_ID = 123456789  # Apni Telegram ID yahan daalein

DB_NAME = "salon_saas.db"

async def add_salon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != SUPER_ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized access! Sirf SaaS Super-Admin is command ko run kar sakta hai.")
        return

    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("⚠️ Usage: `/addsalon SalonName BotToken [LogoURL] [ColorHex]`", parse_mode="Markdown")
            return

        salon_name = args[0]
        bot_token = args[1]
        logo_url = args[2] if len(args) > 2 else "https://via.placeholder.com/80"
        color = args[3] if len(args) > 3 else "#2563eb"

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO salons (salon_name, bot_token) VALUES (?, ?)", (salon_name, bot_token))
        salon_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO salon_branding (salon_id, logo_url, primary_color) VALUES (?, ?, ?)", 
            (salon_id, logo_url, color)
        )
        conn.commit()
        conn.close()

        await update.message.reply_text(
            f"🎉 *Salon Onboarded Successfully!*\n\n"
            f"• *Salon ID:* `{salon_id}`\n"
            f"• *Name:* {salon_name}\n"
            f"• *Theme Color:* `{color}`",
            parse_mode="Markdown"
        )
    except sqlite3.IntegrityError:
        await update.message.reply_text("❌ Error: Ye Bot Token pehle se exist karta hai.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error adding salon: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(ADMIN_BOT_TOKEN).build()
    app.add_handler(CommandHandler("addsalon", add_salon))
    print("👑 SaaS Master Admin Bot Running...")
    app.run_polling()