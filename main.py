import os
from fastapi import FastAPI
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از .env
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
APP_URL = os.getenv("APP_URL")

app = FastAPI()


# --- توابع ربات ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! 🌸\nمن دستیار هوشمند محضرباشی هستم.\nسوال حقوقی داری؟ بپرس تا راهنماییت کنم."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "برای دریافت پاسخ حقوقی، کافیست سوالت را تایپ کنی.\n"
        "در صورت نیاز، به سایت محضرباشی هم راهنمایی‌ات می‌کنم 🌐"
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(
        f"🔹 پرسشت دریافت شد:\n{text}\n\nبه زودی پاسخ داده می‌شود."
    )


# --- تنظیم اپلیکیشن تلگرام ---
telegram_app = ApplicationBuilder().token(TOKEN).build()

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("help", help_command))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


# --- Webhook ---
@app.on_event("startup")
async def on_startup():
    webhook_url = f"{APP_URL}/webhook/{TOKEN}"
    await telegram_app.bot.set_webhook(webhook_url)
    print(f"✅ Webhook set to {webhook_url}")


@app.post(f"/webhook/{TOKEN}")
async def webhook(update: dict):
    update = Update.de_json(update, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}


@app.get("/")
def home():
    return {"status": "OK", "bot": "Mahzarbashi Assistant"}
