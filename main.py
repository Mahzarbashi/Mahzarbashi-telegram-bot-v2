import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from gtts import gTTS
import asyncio

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN در محیط Render تعریف نشده!")

application = Application.builder().token(TOKEN).build()

# --- هندلر /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋 من ربات محضرباشی‌ام!\nسؤالت رو بنویس تا راهنماییت کنم."
    )

# --- هندلر پاسخ به پیام ---
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    response_text = f"پاسخ خودکار: درباره‌ی «{text}» به‌زودی توضیح داده می‌شود."
    await update.message.reply_text(response_text)
    tts = gTTS(response_text, lang="fa")
    tts.save("reply.mp3")
    await update.message.reply_voice(voice=open("reply.mp3", "rb"))

# --- افزودن هندلرها ---
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

# --- اجرای Long Polling ---
async def main():
    await application.initialize()
    await application.start()
    print("✅ ربات با Long Polling فعال شد و آماده پاسخگویی است")
    await application.updater.start_polling()
    await asyncio.Event().wait()  # نگه داشتن ربات

if __name__ == "__main__":
    asyncio.run(main())
