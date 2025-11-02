import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import nest_asyncio
import os

nest_asyncio.apply()

# 🔹 تنظیمات لاگ برای بررسی راحت‌تر خطاها
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 🔹 توکن ربات (از BotFather)
TOKEN = os.getenv("BOT_TOKEN", "932785959:AAGR9Z_g87RUwuGygcx76lPG5i725jT52TM")

# 🔹 دستور start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام 👋 من ربات محضرباشی هستم. چطور می‌تونم کمکتون کنم؟")

# 🔹 پاسخ به پیام‌های عادی
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text(f"شما گفتید: {user_text}")

# 🔹 تابع اصلی برای راه‌اندازی ربات
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
