from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from gtts import gTTS
from fastapi import FastAPI, Request
import nest_asyncio
import asyncio
import os

# فعال‌سازی async در محیط‌های ترکیبی
nest_asyncio.apply()

# 🌐 وب‌سرور FastAPI برای Render
app = FastAPI()

# 🔑 توکن ربات (تست مستقیم)
BOT_TOKEN = "8249435097:AAEqSwTL8Ah8Kfyzo9Z_iQE97OVUViXtOmY"

# 📢 تابع پاسخ به پیام‌ها
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    response_text = f"سلام {update.effective_user.first_name} 🌸\nپیامت رسید:\n«{user_text}»"

    try:
        tts = gTTS(response_text, lang="fa")
        tts.save("reply.mp3")
        await update.message.reply_audio(audio=open("reply.mp3", "rb"), caption=response_text)
        os.remove("reply.mp3")
    except Exception as e:
        await update.message.reply_text(response_text + f"\n⚠️ خطا در تولید صدا: {e}")

# ساخت اپلیکیشن تلگرام
application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

# آدرس وبهوک
WEBHOOK_URL = "https://mahzarbashi-telegram-bot-v2-1.onrender.com"

@app.on_event("startup")
async def startup():
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    print("✅ Webhook set successfully!")

@app.post(f"/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

@app.get("/")
def home():
    return {"status": "Mahzarbashi Bot is alive ✅"}

# اجرای سرور
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
