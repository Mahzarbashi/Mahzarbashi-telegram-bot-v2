import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ContextTypes
)
from gtts import gTTS
import tempfile
import requests
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# پاسخ‌های FAQ نمونه (قابل توسعه و ذخیره در دیتابیس)
FAQ_RESPONSES = {
    "سوال ۱": "پاسخ سوال ۱ به زبان ساده و کامل.",
    "سوال ۲": "پاسخ سوال ۲ به زبان ساده و کامل."
}

# منوی شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("سوالات رایج", callback_data='faq')],
        [InlineKeyboardButton("مشاوره حقوقی", url="https://mahzarbashi.com")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام! من ربات محضرباشی هستم 🤖\n"
        "من می‌تونم به سوالات حقوقی شما پاسخ بدم و شما رو به مشاوره هدایت کنم.",
        reply_markup=reply_markup
    )

# مدیریت دکمه‌ها
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'faq':
        keyboard = [[InlineKeyboardButton(q, callback_data=f"faq_{q}")] for q in FAQ_RESPONSES.keys()]
        await query.edit_message_text("لطفا سوال خود را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data.startswith("faq_"):
        question = query.data.replace("faq_", "")
        answer = FAQ_RESPONSES.get(question, "متاسفم، پاسخی برای این سوال ندارم.")
        await query.edit_message_text(f"سوال: {question}\n\nپاسخ: {answer}")
        # تولید پاسخ صوتی و ارسال
        tts = gTTS(answer, lang='fa')
        with tempfile.NamedTemporaryFile(suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            await query.message.reply_audio(open(tmp_file.name, 'rb'))

# پاسخ به پیام‌های متنی ساده
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "سلام" in text:
        await update.message.reply_text(
            "سلام! خوش اومدی 😊 می‌تونی از من سوالات حقوقی بپرسی یا به مشاوره هدایت بشی."
        )
    else:
        await update.message.reply_text(
            "متاسفم، من متوجه نشدم. لطفا یکی از گزینه‌ها را از منو انتخاب کن."
        )

# اجرای ربات
if __name__ == '__main__':
    if not TOKEN:
        print("توکن ربات پیدا نشد! لطفا فایل .env بساز و TELEGRAM_TOKEN را قرار بده.")
        exit()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("ربات محضرباشی در حال اجراست...")
    app.run_polling()
