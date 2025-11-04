# main.py
import os
import tempfile
from typing import Dict

from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from gtts import gTTS
from dotenv import load_dotenv

# ---------- تنظیم و بارگذاری متغیرها ----------
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
APP_URL = os.getenv("APP_URL")  # مثل: https://mahzarbashi-telegram-bot-v2-1.onrender.com

if not TOKEN or not APP_URL:
    raise RuntimeError("لطفاً TELEGRAM_TOKEN و APP_URL را در .env مقداردهی کن.")

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{APP_URL}{WEBHOOK_PATH}"

# ---------- داده‌های پرسش‌ و پاسخ (FAQ) ----------
# اینجا پاسخ‌های رایج حقوقی را قرار دادم؛ می‌تونی افزوده یا اصلاحشون کنی.
FAQ_RESPONSES: Dict[str, str] = {
    "مهریه": (
        "مهریه حق مالی زن است. به طور کلی می‌توان آن را نقداً یا غیرنقدی تعیین کرد. "
        "زن هر زمان بخواهد می‌تواند آن را مطالبه کند مگر در مواردی که در عقدنامه شرط دیگری ذکر شده باشد."
    ),
    "طلاق توافقی": (
        "طلاق توافقی زمانی است که زن و مرد بر سر شروط طلاق به توافق برسند و با مراجعه به دفاتر خدمات قضایی یا با تنظیم دادخواست، روند طلاق را طی کنند."
    ),
    "حضانت": (
        "قانون ایران برای حضانت فرزند قواعدی دارد؛ معمولاً تا سن مشخصی حضانت با مادر است اما در مواردی دادگاه مصلحت کودک را بررسی می‌کند."
    ),
    "اجاره": (
        "در قرارداد اجاره باید مدت اجاره، مبلغ اجاره‌بها، شرایط تحویل و سایر موارد کلیدی صریحا نوشته شود. اگر اختلافی پیش بیاید، قرارداد مکتوب معمولاً مرجع خواهد بود."
    ),
    "چک": (
        "در صورت برگشتِ چک، شاکی می‌تواند از طریق اجرای ثبت یا طرح شکایت کیفری اقدام کند؛ شرایط و مهلت‌ها و راهکارها بسته به وضعیت متفاوت است."
    ),
    "ارث": (
        "تقسیم ماترک و ارث طبق قواعد شرعی و قوانین مربوطه انجام می‌شود؛ وراث، سهم‌الارث و نحوه اجرا ممکن است نیاز به مشورت حقوقی داشته باشد."
    ),
    # می‌تونی اینجا موارد بیشتری اضافه کنی
}

# ---------- ایجاد اپ FastAPI و اپ تلگرام ----------
app = FastAPI()
telegram_app = ApplicationBuilder().token(TOKEN).build()


# ---------- توابع کمکی ----------
def shorten_or_link(answer: str) -> str:
    """
    اگر پاسخ بیش از 10 خط (تقریبی) شد، یک موجز قرار می‌دهد و لینک سایت را اضافه می‌کند.
    این مرز تقریبی است و براساس خطوط متن (شمارش '\n') عمل می‌کند.
    """
    lines = answer.count("\n") + 1
    if lines > 10 or len(answer.splitlines()) > 10 or len(answer) > 1200:
        brief = answer.split("\n")[0:8]  # چند خط اول
        brief_text = "\n".join(brief).strip()
        brief_text += (
            "\n\nبرای توضیحات کامل‌تر و جزئیات بیشتر، به وب‌سایت محضرباشی مراجعه کن: https://mahzarbashi.ir"
        )
        return brief_text
    return answer


async def reply_text_and_voice(update, text: str):
    """
    ارسال پاسخ متنی و تولید/ارسال فایل صوتی با gTTS (فارسی).
    """
    # اول متن را ارسال می‌کنیم
    await update.message.reply_text(text)

    # سپس فایل صوتی می‌سازیم و ارسال می‌کنیم
    try:
        tts = gTTS(text=text, lang="fa")
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as tmp:
            tts.save(tmp.name)
            # باز کردن فایل بصورت باینری و ارسال (کتابخانه‌ی python-telegram-bot این را پشتیبانی می‌کند)
            with open(tmp.name, "rb") as audio_file:
                await update.message.reply_audio(audio=audio_file)
    except Exception as e:
        # در صورت خطا در تولید صوت، فقط متن را ارسال می‌کنیم و لاگ مینویسیم
        await update.message.reply_text("⚠️ متاسفانه ارسال پیام صوتی ممکن نشد. متن در بالا موجود است.")


# ---------- هندلرها ----------
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    intro = (
        "سلام! 👋 من دستیار حقوقی محضرباشی هستم.\n"
        "ساخته‌شده توسط نسترن بنی‌طبا.\n"
        "هر سؤال حقوقی داری، من با حوصله برات توضیح می‌دم ⚖️"
    )
    await reply_text_and_voice(update, intro)


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip().lower()

    # ابتدا اسراراً بررسی کنیم کاربر به موضوعات حقوقی رایج اشاره کرده یا نه
    matched = None
    for key in FAQ_RESPONSES.keys():
        if key in text:
            matched = key
            break

    if not matched:
        # اگر هیچ موردی یافت نشد، یک پاسخ کوتاه بدهیم که فقط سؤالات حقوقی رایج پاسخ داده می‌شود
        await update.message.reply_text(
            "🙏 متاسفم؛ من فعلاً فقط به سؤالات حقوقی رایج پاسخ می‌دم. موضوع مورد نظرت رو واضح‌تر یا یکی از کلمات زیر رو بگو: "
            + ", ".join(list(FAQ_RESPONSES.keys()))
        )
        return

    answer = FAQ_RESPONSES[matched]
    # اگر خیلی طولانیه خلاصه می‌کنیم و لینک می‌دیم
    rendered_answer = shorten_or_link(answer)
    await reply_text_and_voice(update, rendered_answer)


# ثبت هندلرها در اپ تلگرام
telegram_app.add_handler(CommandHandler("start", start_handler))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))


# ---------- Startup و Shutdown events برای FastAPI ----------
@app.on_event("startup")
async def startup_event():
    # آماده‌سازی اپ تلگرام (initialize + start) و ست کردن وبهوک
    await telegram_app.initialize()
    await telegram_app.start()
    # ست کردن webhook روی مسیر ثابت /webhook
    await telegram_app.bot.set_webhook(f"{WEBHOOK_URL}")
    print(f"✅ Webhook set to {WEBHOOK_URL}")


@app.on_event("shutdown")
async def shutdown_event():
    # پاکسازی و توقف اپ تلگرام
    try:
        await telegram_app.bot.delete_webhook()
    except Exception:
        pass
    await telegram_app.stop()
    await telegram_app.shutdown()


# ---------- مسیر وبهوک ----------
@app.post("/webhook")
async def telegram_webhook(request: Request):
    body = await request.json()
    update = Update.de_json(body, telegram_app.bot)
    # پردازش آپدیت (این تابع هندلرها را اجرا می‌کند)
    await telegram_app.process_update(update)
    return {"ok": True}


# مسیر ساده برای تست سرویس
@app.get("/")
async def index():
    return {"status": "ok", "message": "Mahzarbashi bot is running"}
