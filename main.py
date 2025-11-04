import os
import asyncio
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from gtts import gTTS
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
APP_URL = os.getenv("APP_URL")

if not TOKEN or not APP_URL:
    raise ValueError("❌ مقادیر TELEGRAM_TOKEN یا APP_URL تنظیم نشده است!")

# Initialize Telegram bot
telegram_app = ApplicationBuilder().token(TOKEN).build()

# Initialize FastAPI
app = FastAPI()

# List of simple legal Q&A examples
LEGAL_QA = {
    "چک": "چک یک سند تجاری است که در آن صادرکننده دستور پرداخت وجهی به بانک را صادر می‌کند.",
    "عقد نکاح": "عقد نکاح قراردادی است بین زن و مرد برای تشکیل خانواده و روابط زناشویی.",
    "وصیت نامه": "وصیت نامه سندی است که فرد در آن دارایی خود را بعد از مرگ بین وراث یا افراد معین تقسیم می‌کند.",
    "مهریه": "مهریه، مالی است که مرد به زن در هنگام عقد نکاح می‌دهد و طلب آن قابل پیگیری قانونی است."
}

# Function to generate voice message
async def generate_voice(text: str):
    tts = gTTS(text=text, lang="fa")
    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    return audio_bytes

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "سلام 👋 من دستیار محضرباشی‌ام، در خدمت شما هستم.\n"
        "سازنده من: نسترن بنی طبا 🌟\n"
        "سوال حقوقی دارید؟ می‌تونید از من بپرسید!"
    )
    await update.message.reply_text(text)

    audio = await generate_voice(text)
    await context.bot.send_audio(chat_id=update.effective_chat.id, audio=audio, filename="intro.mp3")

# Handle messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text.strip()
    answer = LEGAL_QA.get(user_msg)

    if answer:
        if len(answer.split()) > 50:
            answer += f"\nبرای اطلاعات بیشتر به سایت محضرباشی مراجعه کنید: {APP_URL}"
    else:
        answer = f"متأسفم 😔، من فقط می‌توانم به سوالات حقوقی رایج پاسخ بدهم. برای اطلاعات بیشتر به سایت محضرباشی مراجعه کنید: {APP_URL}"

    await update.message.reply_text(answer)

    audio = await generate_voice(answer)
    await context.bot.send_audio(chat_id=update.effective_chat.id, audio=audio, filename="answer.mp3")

# Add handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# FastAPI webhook endpoint
@app.post(f"/{TOKEN}")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Bot is running. Webhook set correctly."}
