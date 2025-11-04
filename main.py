import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from gtts import gTTS
from dotenv import load_dotenv
import asyncio

# بارگذاری متغیرهای محیطی
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
APP_URL = os.getenv("APP_URL")

if not TOKEN or not APP_URL:
    raise ValueError("❌ مقادیر TELEGRAM_TOKEN یا APP_URL تنظیم نشده است!")

# ساخت برنامه تلگرام
telegram_app = ApplicationBuilder().token(TOKEN).build()

# ساخت برنامه FastAPI برای webhook
app = FastAPI()


# 🎙 تابع تبدیل متن به صدا
def text_to_voice(text):
    tts = gTTS(text=text, lang="fa")
    voice_path = "voice.mp3"
    tts.save(voice_path)
    return voice_path


# 🎉 دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "سلام! 👋\n"
        "من دستیار حقوقی محضرباشی‌ام. ساخته شده توسط نسترن بنی‌طبا 🌿\n"
        "می‌تونم به سوالات حقوقی رایجت جواب بدم. فقط کافیه سوالت رو بنویسی 🧾"
    )
    await update.message.reply_text(welcome_text)
    voice_path = text_to_voice("سلام! من دستیار حقوقی محضرباشی هستم. ساخته‌ی نسترن بنی‌طبا. خوش اومدی!")
    await update.message.reply_voice(voice=open(voice_path, "rb"))


# 🎯 تابع پاسخ به سوالات حقوقی
async def reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text.lower()

    # چند مثال از پاسخ‌های نمونه (می‌تونیم بعداً گسترش بدیم)
    responses = {
        "مهریه": "مهریه حقی مالیه که بعد از عقد به زن تعلق می‌گیره و هر زمان که بخواد می‌تونه اون رو مطالبه کنه.",
        "طلاق": "طلاق به درخواست زن فقط در شرایط خاصی مثل عُسر و حرج یا وکالت در طلاق ممکنه. بهتره با وکیل مشورت بشه.",
        "چک": "اگر چک برگشت خورده باشه، می‌تونی از طریق سامانه صیاد یا دادگاه شکایت کنی تا حکم جلب صادر بشه.",
        "اجاره": "قرارداد اجاره حتماً باید مدت و مبلغ اجاره مشخص داشته باشه. در غیر این صورت باطل محسوب میشه.",
        "شکایت": "برای ثبت شکایت، باید به دفاتر خدمات قضایی مراجعه و دادخواست تنظیم کنی."
    }

    answer = None
    for key, value in responses.items():
        if key in user_question:
            answer = value
            break

    if not answer:
        answer = (
            "سوالت حقوقیه و نیاز به بررسی دقیق داره 🌿 "
            "برای توضیحات کامل‌تر به سایت محضرباشی سر بزن:\n"
            "🔗 https://mahzarbashi.ir"
        )

    # اگر جواب خیلی طولانی بود → هدایت به سایت
    if len(answer) > 400:
        answer += "\n\n📚 ادامه مطلب در سایت محضرباشی موجوده."

    await update.message.reply_text(answer)

    # پاسخ صوتی هم ارسال کن
    voice_path = text_to_voice(answer)
    await update.message.reply_voice(voice=open(voice_path, "rb"))


# اضافه کردن هندلرها
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_message))


# 📡 مسیر وبهوک
@app.post("/{token}")
async def telegram_webhook(request: Request, token: str):
    if token == TOKEN:
        data = await request.json()
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.process_update(update)
        return {"ok": True}
    else:
        return {"error": "توکن اشتباه است."}


# 🚀 اجرای بات با webhook
async def run_webhook():
    webhook_url = f"{APP_URL}/{TOKEN}"
    await telegram_app.bot.set_webhook(webhook_url)
    print(f"✅ Webhook set to: {webhook_url}")
    await telegram_app.run_polling()


if __name__ == "__main__":
    print("🚀 Bot is running...")
    asyncio.run(run_webhook())
