import os
import asyncio
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from gtts import gTTS
from dotenv import load_dotenv

# بارگذاری فایل env
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
APP_URL = os.getenv("APP_URL")

if not TOKEN or not APP_URL:
    raise ValueError("❌ مقادیر TELEGRAM_TOKEN یا APP_URL تنظیم نشده است!")

# ساخت اپلیکیشن FastAPI
app = FastAPI()

# ساخت بات تلگرام
telegram_app = ApplicationBuilder().token(TOKEN).build()

# 🎤 تابع تولید صوت از متن
def text_to_voice(text, filename="reply.mp3"):
    tts = gTTS(text=text, lang='fa')
    tts.save(filename)
    return filename

# 🎯 دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "سلام 👋 من دستیار محضرباشی‌ام، در خدمت شما هستم. بپرس ببینم چطور می‌تونم کمکت کنم 😊"
    await update.message.reply_text(msg)

# 💬 پاسخ به پیام‌های کاربر
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()

    # پاسخ‌های ساده حقوقی
    if "مهریه" in user_message:
        reply = "مهریه حقی است که در عقدنامه ثبت می‌شود و زن هر زمان بخواهد می‌تواند آن را مطالبه کند."
    elif "طلاق" in user_message:
        reply = "طلاق زمانی ثبت می‌شود که حکم دادگاه صادر شود و تشریفات قانونی رعایت گردد."
    elif "حضانت" in user_message:
        reply = "حضانت فرزند تا ۷ سالگی با مادر و پس از آن با پدر است مگر دادگاه خلافش را تشخیص دهد."
    elif "سند" in user_message:
        reply = "سند رسمی در دفترخانه تنظیم می‌شود و اعتبار بیشتری از سند عادی دارد."
    else:
        reply = "سؤال حقوقی‌ت رو بپرس تا راهنماییت کنم 🌿"

    # ارسال پاسخ متنی
    await update.message.reply_text(reply)

    # اگر پاسخ کوتاه است، نسخه صوتی‌اش را هم بفرست 🎧
    if len(reply) < 200:
        voice_file = text_to_voice(reply)
        with open(voice_file, "rb") as voice:
            await update.message.reply_voice(voice)
        os.remove(voice_file)

# 📦 افزودن هندلرها
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# 🌐 مسیر وبهوک
@app.post("/webhook/{token}")
async def webhook(request: Request, token: str):
    if token != TOKEN:
        return {"error": "Invalid token"}

    update = Update.de_json(await request.json(), telegram_app.bot)
    await telegram_app.initialize()
    await telegram_app.process_update(update)
    return {"ok": True}

# 🏠 مسیر تست
@app.get("/")
async def home():
    return {"status": "✅ Bot is live", "creator": "Nastaran Bani Taba"}
