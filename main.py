import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from gtts import gTTS
import uvicorn
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# ساخت برنامه‌ها
app = FastAPI()
telegram_app = Application.builder().token(TOKEN).build()

# -------------------- دستورات ربات --------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "سلام 👋 من دستیار حقوقی محضرباشی‌ام.\n"
        "سازنده‌م نسترن بنی‌طباست 💫\n"
        "سؤالات حقوقی‌تو ازم بپرس، با لحن ساده و صمیمی جواب می‌دم.\n"
        "اگه توضیح طولانی شد، می‌فرستمت سایت محضرباشی 🌐 mahzarbashi.ir"
    )
    await update.message.reply_text(text)


async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text.strip()

    if "طلاق" in question:
        answer = "طلاق توافقی یعنی هر دو نفر با رضایت جدا می‌شن و مدارک رو با هم تحویل می‌دن."
    elif "مهریه" in question:
        answer = "مهریه حق زن هست و هر زمان بخواد می‌تونه از طریق اجرای ثبت یا دادگاه درخواست بده."
    elif "حضانت" in question:
        answer = "حضانت بچه تا ۷ سالگی معمولاً با مادره و بعدش با پدر، ولی قاضی شرایط خاص رو هم بررسی می‌کنه."
    else:
        answer = "برای پاسخ دقیق‌تر به این سؤال بهتره بری به سایت 🌐 mahzarbashi.ir"

    await update.message.reply_text(answer)

    # تولید صوت از پاسخ
    try:
        tts = gTTS(answer, lang="fa")
        tts.save("voice.mp3")
        with open("voice.mp3", "rb") as f:
            await update.message.reply_voice(f)
    except Exception as e:
        print("خطا در تولید صوت:", e)


# -------------------- هندلرها --------------------
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

# -------------------- وب‌هوک --------------------
@app.post("/{token}")
async def webhook(request: Request, token: str):
    if token == TOKEN:
        data = await request.json()
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.process_update(update)
        return {"ok": True}
    return {"error": "توکن اشتباه است"}

@app.get("/")
async def home():
    return {"status": "Mahzarbashi bot is running 🚀"}


# -------------------- اجرای لوکال --------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
