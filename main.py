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

# ---- Telegram App ----
telegram_app = ApplicationBuilder().token(TOKEN).build()

# ---- دستور شروع ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام 👋 من دستیار محضرباشی‌ام، کمکت می‌کنم به سؤالات حقوقی جواب بدی 😊")

telegram_app.add_handler(CommandHandler("start", start))

# ---- FastAPI App ----
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

@app.post(f"/webhook/{TOKEN}")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}
