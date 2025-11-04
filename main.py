import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from gtts import gTTS

# بارگذاری متغیرهای محیطی
TOKEN = os.getenv("TELEGRAM_TOKEN")
APP_URL = os.getenv("APP_URL")

if not TOKEN or not APP_URL:
    raise ValueError("❌ مقادیر TELEGRAM_TOKEN یا APP_URL تنظیم نشده است!")

# پیام خوش‌آمد متنی
WELCOME_TEXT = """سلام! 👋
من «دستیار محضرباشی‌»ام 😊
یه همراه هوشمند که ساخته‌ی نسترن بنی‌طبا هستم، تا پرسش‌های حقوقی‌ت رو ساده، دقیق و بدون دردسر جواب بدم ⚖️
هر وقت سوالی درباره‌ی قوانین یا کارهای دفترخانه داشتی، من اینجام تا کمکت کنم 💬
"""

# مسیر ذخیره فایل صوتی
AUDIO_FILE = "welcome.mp3"

# تولید فایل صوتی با gTTS
if not os.path.exists(AUDIO_FILE):
    tts = gTTS(text=WELCOME_TEXT, lang="fa")
    tts.save(AUDIO_FILE)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT)
    await update.message.reply_audio(audio=open(AUDIO_FILE, "rb"))

# پاسخ به سوالات حقوقی رایج
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    # نمونه سوالات رایج (قابل گسترش)
    if "وکالت" in text or "وکیل" in text:
        response = "در مورد وکالت، می‌تونی مراحل و مدارک مورد نیاز رو در سایت محضرباشی ببینی: https://mahzarbashi.onrender.com"
    elif "ازدواج" in text or "طلاق" in text:
        response = "مسائل ازدواج و طلاق شامل قوانین مشخصی هست. برای راهنمایی کامل‌تر، به سایت محضرباشی مراجعه کن."
    else:
        response = "متأسفم، این سوال فراتر از پاسخ کوتاهه. لطفاً به وبسایت محضرباشی سر بزن: https://mahzarbashi.onrender.com"
    
    await update.message.reply_text(response)

# ایجاد اپلیکیشن و هندلرها
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# اجرای ربات
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
