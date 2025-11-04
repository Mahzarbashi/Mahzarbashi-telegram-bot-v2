import os
import logging
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ---- Logging ----
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---- Token & App URL ----
TOKEN = os.getenv("TELEGRAM_TOKEN")
APP_URL = os.getenv("APP_URL")

if not TOKEN or not APP_URL:
    raise ValueError("❌ مقادیر TELEGRAM_TOKEN یا APP_URL تنظیم نشده است!")

# ---- Telegram Application ----
telegram_app = ApplicationBuilder().token(TOKEN).build()

# ---- Commands ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام 👋 من دستیار محضرباشی‌ام، در خدمت شما هستم.")

telegram_app.add_handler(CommandHandler("start", start))

# ---- FastAPI ----
app = FastAPI()

@app.on_event("startup")
async def startup():
    await telegram_app.initialize()
    webhook_url = f"{APP_URL}/webhook/{TOKEN}"
    await telegram_app.bot.set_webhook(url=webhook_url)
    logger.info(f"✅ Webhook set to: {webhook_url}")

@app.on_event("shutdown")
async def shutdown():
    await telegram_app.shutdown()

# ✅ مسیر GET فقط برای تست مرورگر
@app.get("/")
async def home():
    return {"status": "OK", "message": "Mahzarbashi Telegram Bot is running 🚀"}

# ✅ مسیر رسمی برای تلگرام (POST)
@app.post(f"/webhook/{TOKEN}")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}
