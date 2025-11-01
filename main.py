import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from gtts import gTTS

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN در محیط Render تعریف نشده!")

app = FastAPI()
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام 👋 من ربات محضرباشی‌ام!\nسؤالت رو بنویس تا راهنماییت کنم.")

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    response_text = f"پاسخ خودکار: درباره‌ی «{text}» به‌زودی توضیح داده می‌شود."
    await update.message.reply_text(response_text)
    tts = gTTS(response_text, lang="fa")
    tts.save("reply.mp3")
    await update.message.reply_voice(voice=open("reply.mp3", "rb"))

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

@app.post(f"/{TOKEN}")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

@app.get("/")
async def home():
    return {"status": "Bot is running ✅"}
