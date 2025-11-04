import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
APP_URL = os.getenv("APP_URL")

app = FastAPI()
application = ApplicationBuilder().token(TOKEN).build()

# ---------------------------
# معرفی ربات هنگام start
# ---------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "سلام 🌸\n"
        "من دستیار هوشمند **محضرباشی** هستم 🤖\n"
        "ساخته شده توسط *نسترن بنی‌طبا* 💼\n\n"
        "سؤالاتت درباره‌ی قوانین و موضوعات حقوقی روزمره رو ازم بپرس تا با زبون ساده جواب بدم 👇"
    )
    await update.message.reply_text(text)

# ---------------------------
# تولید پاسخ متنی و صوتی
# ---------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()

    # اگر سوال حقوقی بود پاسخ بده
    if any(keyword in user_text for keyword in ["طلاق", "مهریه", "وکالت", "سند", "قرارداد", "شکایت", "ارث", "ملک", "اجاره", "طلاق توافقی"]):
        reply_text = (
            "سؤال خوبیه 🌷\n"
            "ولی قبل از هر چیز بدون که پاسخ‌ها جنبه‌ی عمومی دارن و جای مشاوره‌ی تخصصی رو نمی‌گیرن.\n\n"
            "در مورد «{}» باید بدونی که بسته به شرایط، قوانین فرق می‌کنن.\n"
            "برای توضیح کامل‌تر حتماً به وب‌سایت محضرباشی سر بزن 👇\n"
            "https://mahzarbashi.ir"
        ).format(user_text[:20])

        # پاسخ صوتی
        tts = gTTS(text=reply_text, lang='fa')
        voice_path = f"voice_{update.message.chat_id}.mp3"
        tts.save(voice_path)

        await update.message.reply_text(reply_text)
        await update.message.reply_voice(voice=open(voice_path, 'rb'))

        os.remove(voice_path)

    else:
        await update.message.reply_text("سؤالات حقوقی بپرس عزیزم تا راهنماییت کنم 🌼")

# ---------------------------
# اتصال هندلرها
# ---------------------------
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ---------------------------
# FastAPI Route برای Webhook
# ---------------------------
@app.post("/{token}")
async def webhook(request: Request, token: str):
    if token == TOKEN:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return {"ok": True}
    return {"ok": False}

@app.get("/")
async def home():
    return {"status": "Mahzarbashi bot is running 🚀"}

# ---------------------------
# اجرای خودکار در Render
# ---------------------------
if __name__ == "__main__":
    import asyncio
    from telegram import Bot

    async def main():
        bot = Bot(token=TOKEN)
        webhook_url = f"{APP_URL}/{TOKEN}"
        await bot.delete_webhook()
        await bot.set_webhook(url=webhook_url)
        print(f"Webhook set to: {webhook_url}")
        await application.run_polling()

    asyncio.run(main())
