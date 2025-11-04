import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from gtts import gTTS
from dotenv import load_dotenv
import asyncio

# بارگذاری .env
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
APP_URL = os.getenv("APP_URL")

if not TOKEN or not APP_URL:
    raise ValueError("❌ مقادیر TELEGRAM_TOKEN یا APP_URL تنظیم نشده است!")

# ساخت برنامه تلگرام (بدون run_polling)
telegram_app = ApplicationBuilder().token(TOKEN).build()

# ساخت برنامه FastAPI
app = FastAPI()


# 🎙 تابع تبدیل متن به صدا
def text_to_voice(text):
    tts = gTTS(text=text, lang="fa")
    voice_path = "voice.mp3"
    tts.save(voice_path)
    return voice_path


# 🟢 دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "سلام! 👋 من دستیار حقوقی محضرباشی‌ام، ساخته‌شده توسط نسترن بنی‌طبا 🌿\n"
        "می‌تونم سوالات حقوقی روزمره‌ت رو جواب بدم، فقط بپرس 😊"
    )
    await update.message.reply_text(welcome_text)
    voice_path = text_to_voice("سلام! من دستیار حقوقی محضرباشی هستم. ساخته‌ی نسترن بنی‌طبا. خوش اومدی!")
    await update.message.reply_voice(voice=open(voice_path, "rb"))


# 💬 پاسخ به سوالات
async def reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()

    responses = {
        "مهریه": "مهریه حق مالیه که بعد از عقد به زن تعلق می‌گیره و هر زمان بخواد می‌تونه مطالبه‌ش کنه.",
        "طلاق": "طلاق به درخواست زن فقط در شرایط خاصی مثل عسر و حرج یا وکالت در طلاق ممکنه.",
        "چک": "برای چک برگشتی می‌تونی از طریق سامانه صیاد یا دادگاه اقدام کنی تا حکم جلب صادر بشه.",
        "اجاره": "در قرارداد اجاره باید مدت و مبلغ مشخص باشه، وگرنه قرارداد باطله.",
        "شکایت": "برای ثبت شکایت باید از دفاتر خدمات قضایی دادخواست بدی."
    }

    answer = next((v for k, v in responses.items() if k in text), None)

    if not answer:
        answer = (
            "سوالت حقوقیه و نیاز به بررسی دقیق‌تر داره 🌿 "
            "برای توضیحات کامل‌تر می‌تونی بری سایت محضرباشی:\n"
            "🔗 https://mahzarbashi.ir"
        )

    await update.message.reply_text(answer)
    voice_path = text_to_voice(answer)
    await update.message.reply_voice(voice=open(voice_path, "rb"))


# افزودن هندلرها
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_message))


# 📡 مسیر webhook برای Telegram
@app.post("/{token}")
async def webhook(request: Request, token: str):
    if token == TOKEN:
        data = await request.json()
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.process_update(update)
        return {"ok": True}
    return {"error": "توکن اشتباه است."}


# 🚀 تنظیم webhook در هنگام بالا آمدن
@app.on_event("startup")
async def set_webhook():
    webhook_url = f"{APP_URL}/{TOKEN}"
    await telegram_app.bot.set_webhook(webhook_url)
    print(f"✅ Webhook set to: {webhook_url}")
