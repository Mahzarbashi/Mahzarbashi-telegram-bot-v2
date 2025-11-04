import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ------------------------------
# 🔹 فعال کردن لاگ‌ها برای بررسی خطاها
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ------------------------------
# 🔹 گرفتن اطلاعات از Environment
TOKEN = os.getenv("TELEGRAM_TOKEN")
APP_URL = os.getenv("APP_URL")

if not TOKEN or not APP_URL:
    raise ValueError("❌ مقادیر TELEGRAM_TOKEN یا APP_URL تنظیم نشده است!")

# ------------------------------
# 🔹 دستور start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋\nمن دستیار هوشمند محضرباشی‌ام 🌿\n"
        "هر سوالی درباره‌ی امور محضری داری بپرس، کمکت می‌کنم 💬"
    )

# ------------------------------
# 🔹 پاسخ به پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "سلام" in text:
        await update.message.reply_text("سلام خوش اومدی 🌸")
    elif "محضر" in text or "سند" in text:
        await update.message.reply_text("در مورد سند یا کارهای محضری بپرس تا راهنماییت کنم 🖋️")
    else:
        await update.message.reply_text("متوجه منظورت نشدم 🧐 یه کم واضح‌تر بگو لطفاً.")

# ------------------------------
# 🔹 ساخت اپلیکیشن تلگرام
async def main():
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    # دستورها و پیام‌ها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # تنظیم Webhook
    webhook_url = f"{APP_URL}/webhook/{TOKEN}"
    await app.bot.set_webhook(webhook_url)
    print(f"✅ Webhook set to: {webhook_url}")

    # اجرای وب‌سرور
    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", "8080")),
        url_path=f"/webhook/{TOKEN}"
    )

# ------------------------------
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
