from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋 من دستیار حقوقی محضرباشی‌ام. می‌تونم به سؤالات حقوقی روزمره‌ت جواب بدم.\n"
        "👩🏻‍💼 سازنده من: نسترن بنی‌طبا\n"
        "بپرس تا راهنماییت کنم."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سؤالتو بپرس تا در حد قوانین ایران راهنماییت کنم 🌿")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()

    if "طلاق" in user_text:
        await update.message.reply_text("در طلاق توافقی، هر دو طرف باید در دادگاه حضور پیدا کنن و توافق‌نامه رسمی ارائه بدن.")
    elif "مهریه" in user_text:
        await update.message.reply_text("مهریه حق زن هست و حتی بعد از طلاق هم قابل مطالبه‌ست مگر اینکه خودش ببخشه.")
    else:
        await update.message.reply_text("سؤالت مشخص نیست، لطفاً دقیق‌تر بپرس 💬")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path=TOKEN,
        webhook_url=f"https://mahzarbashi-telegram-bot-v2-1.onrender.com/{TOKEN}"
    )
