import os
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from gtts import gTTS
import tempfile
import logging

# تنظیمات لاگ
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# توکن ربات از محیط
TOKEN = os.getenv("BOT_TOKEN")

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام 👋 من ربات محضرباشی هستم.\nسؤالت رو بنویس تا راهنماییت کنم 🌿")

# پاسخ‌دهی خودکار
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    response_text = f"پاسخت دربارهٔ: {user_text}\nدر حال حاضر من فقط نسخهٔ آزمایشی هستم 🌱"

    # اول پاسخ متنی بفرسته
    await update.message.reply_text(response_text)

    # تلاش برای ساخت فایل صوتی فارسی
    try:
        tts = gTTS(text=response_text, lang="fa", slow=False, tld="com")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            await update.message.reply_voice(voice=InputFile(tmp_file.name))
    except Exception as e:
        logging.warning(f"TTS error: {e}")
        await update.message.reply_text("فعلاً امکان ارسال صوت وجود ندارد 🎧")

# راه‌اندازی ربات
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

    # اجرای وب‌هوک برای Render
    port = int(os.environ.get("PORT", 10000))
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TOKEN,
        webhook_url=f"https://mahzarbashi-telegram-bot-v2-1.onrender.com/{TOKEN}"
    )

if __name__ == "__main__":
    main()
