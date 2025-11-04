import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from gtts import gTTS
import asyncio

# گرفتن توکن از .env
TOKEN = os.getenv("BOT_TOKEN")

# ساخت اپلیکیشن‌ها
app = FastAPI()
telegram_app = ApplicationBuilder().token(TOKEN).build()

# --- معرفی و شروع ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "سلام 👋 من دستیار حقوقی محضرباشی‌ام.\n"
        "سازنده‌م نسترن بنی‌طباست 💫\n"
        "سؤالات حقوقی‌تو ازم بپرس، سعی می‌کنم ساده و دقیق جواب بدم.\n"
        "اگه توضیح طولانی شد، لینک سایت محضرباشی رو می‌فرستم 🌐 mahzarbashi.ir"
    )
    await update.message.reply_text(text)


# --- پاسخ به سؤال‌ها ---
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text.strip()

    if "طلاق" in question:
        answer = "برای طلاق توافقی باید هر دو طرف رضایت داشته باشن و مدارک کامل باشه."
    elif "مهریه" in question:
        answer = "مهریه حق زوجه‌ست و هر زمان بخواد می‌تونه مطالبه کنه."
    elif "حضانت" in question:
        answer = "حضانت تا ۷ سالگی با مادر و بعد از اون با پدره، ولی دادگاه ممکنه شرایط خاص رو هم در نظر بگیره."
    else:
        answer = "سؤال خوبی پرسیدی! برای توضیح کامل‌تر لطفاً به سایت محضرباشی سر بزن 🌐 mahzarbashi.ir"

    await update.message.reply_text(answer)

    # --- تولید پاسخ صوتی ---
    try:
        tts = gTTS(answer, lang="fa")
        tts.save("voice.mp3")
        with open("voice.mp3", "rb") as voice:
            await update.message.reply_voice(voice)
    except Exception as e:
        print("خطا در تولید صوت:", e)


# --- اضافه کردن هندلرها ---
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))


# --- وبهوک FastAPI ---
@app.post("/{token}")
async def webhook(request: Request, token: str):
    if token == TOKEN:
        data = await request.json()
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.process_update(update)
        return {"ok": True}
    return {"error": "Invalid token"}


@app.get("/")
def home():
    return {"status": "Mahzarbashi bot is running 🚀"}


# --- اجرای سرور ---
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
