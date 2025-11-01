import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from gtts import gTTS
import asyncio

# --- توکن از Environment ---
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN در محیط Render تعریف نشده!")

# --- FastAPI ---
app = FastAPI()

# --- اپلیکیشن تلگرام ---
application = Application.builder().token(TOKEN).build()

# --- هندلر دستور /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋 من ربات محضرباشی‌ام!\nسؤالت رو بنویس تا راهنماییت کنم."
    )

# --- هندلر پاسخ به متن ---
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    response_text = f"پاسخ خودکار: درباره‌ی «{text}» به‌زودی توضیح داده می‌شود."

    await update.message.reply_text(response_text)

    # پاسخ صوتی
    tts = gTTS(response_text, lang="fa")
    tts.save("reply.mp3")
    await update.message.reply_voice(voice=open("reply.mp3", "rb"))

# --- افزودن هندلرها ---
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

# --- مسیر FastAPI وبهوک ---
@app.post(f"/{TOKEN}")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

# --- مسیر تست ---
@app.get("/")
async def home():
    return {"status": "Bot is running ✅"}

# --- وبهوک را یک بار ست می‌کنیم ---
async def set_webhook_once():
    render_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    await application.initialize()
    await application.bot.set_webhook(url=render_url)
    print(f"✅ Webhook set to: {render_url}")

# --- اجرای برنامه ---
if __name__ == "__main__":
    # uvicorn خودش AsyncIO loop اجرا می‌کنه، بنابراین asyncio.run() لازم نیست
    import uvicorn

    # قبل از شروع uvicorn، وبهوک را ست می‌کنیم
    asyncio.get_event_loop().run_until_complete(set_webhook_once())

    uvicorn.run(app, host="0.0.0.0", port=10000)
