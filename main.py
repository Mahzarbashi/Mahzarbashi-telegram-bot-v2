import os
import asyncio
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from gtts import gTTS

# --- دریافت توکن از محیط ---
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN در محیط تعریف نشده! لطفاً در Render مقدارش را تنظیم کن.")

# --- ساخت برنامه FastAPI ---
app = FastAPI()

# --- ساخت برنامه تلگرام ---
application = Application.builder().token(TOKEN).build()


# --- فرمان /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام 👋 من ربات محضرباشی‌ام!\nسؤالت رو بنویس تا راهنماییت کنم.")


# --- پاسخ خودکار ---
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    response = f"پاسخ خودکار: درباره‌ی «{text}» به‌زودی توضیح داده می‌شود."

    # پاسخ متنی
    await update.message.reply_text(response)

    # پاسخ صوتی
    tts = gTTS(response, lang="fa")
    tts.save("reply.mp3")
    await update.message.reply_voice(voice=open("reply.mp3", "rb"))


# --- اضافه کردن هندلرها ---
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))


# --- مسیر تست (GET) ---
@app.get("/")
async def home():
    return {"status": "Bot is running ✅"}


# --- مسیر وبهوک (POST) ---
@app.post(f"/{TOKEN}")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}


# --- اجرای اصلی ---
async def start_bot():
    await application.initialize()
    await application.start()
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    await application.bot.set_webhook(url=webhook_url)
    print(f"✅ Webhook set to: {webhook_url}")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(start_bot())
