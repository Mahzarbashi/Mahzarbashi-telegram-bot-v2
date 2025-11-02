import os
import tempfile
from flask import Flask, request
from gtts import gTTS
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv

# بارگذاری متغیرها از .env
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN", "8249435097:AAEqSwTL8Ah8Kfyzo9Z_iQE97OVUViXtOmY")
APP_URL = os.getenv("APP_URL", "https://mahzarbashi.onrender.com")

# ساخت اپلیکیشن Flask برای Webhook
app = Flask(__name__)

# پاسخ‌های سوالات رایج
FAQ_RESPONSES = {
    "مهریه": "طبق قانون ایران، مهریه حق زن است و هر زمان بخواهد می‌تواند آن را مطالبه کند.",
    "طلاق توافقی": "در طلاق توافقی، زوجین با توافق درباره مهریه، حضانت و سایر موارد به دادگاه مراجعه می‌کنند.",
    "حضانت فرزند": "تا ۷ سالگی حضانت با مادر است و بعد از آن دادگاه بر اساس مصلحت کودک تصمیم می‌گیرد.",
}

# ساخت اپ اصلی تلگرام
application = Application.builder().token(BOT_TOKEN).build()


# فرمان /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📚 سوالات رایج", callback_data="faq")],
        [InlineKeyboardButton("🌐 مراجعه به وبسایت محضرباشی", url="https://mahzarbashi.com")],
    ]
    await update.message.reply_text(
        "سلام! 👋\nمن ربات رسمی محضرباشی هستم.\n"
        "می‌تونم به سوالات حقوقی شما پاسخ بدم یا شما رو برای مشاوره به سایت هدایت کنم.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# دکمه‌های منو
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "faq":
        keyboard = [
            [InlineKeyboardButton(q, callback_data=f"faq_{q}")]
            for q in FAQ_RESPONSES.keys()
        ]
        await query.edit_message_text(
            "📖 لطفاً موضوع مورد نظر را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith("faq_"):
        question = query.data.replace("faq_", "")
        answer = FAQ_RESPONSES.get(question, "متاسفم، هنوز پاسخی برای این موضوع ثبت نشده است.")
        await query.edit_message_text(f"📘 {question}\n\n{answer}")

        # تولید فایل صوتی پاسخ و ارسال
        tts = gTTS(answer, lang="fa")
        with tempfile.NamedTemporaryFile(suffix=".mp3") as tmp:
            tts.save(tmp.name)
            await query.message.reply_audio(audio=open(tmp.name, "rb"))


# پاسخ پیام‌های متنی معمولی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "سلام" in text:
        await update.message.reply_text("سلام! 😊 خوش اومدی. از منو گزینه مورد نظرت رو انتخاب کن.")
    elif "مهریه" in text:
        await update.message.reply_text(FAQ_RESPONSES["مهریه"])
    elif "طلاق" in text:
        await update.message.reply_text(FAQ_RESPONSES["طلاق توافقی"])
    else:
        await update.message.reply_text("متوجه نشدم 🌿 لطفاً از منوی اصلی یکی از گزینه‌ها رو انتخاب کن.")


# تنظیم Webhook
@app.route("/setwebhook", methods=["GET"])
def set_webhook():
    webhook_url = f"{APP_URL}/{BOT_TOKEN}"
    success = application.bot.set_webhook(url=webhook_url)
    if success:
        return f"Webhook تنظیم شد ✅\n{webhook_url}"
    return "خطا در تنظیم Webhook ❌", 500


# مسیر دریافت آپدیت‌ها از تلگرام
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok", 200


# ثبت هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# اجرای Flask برای Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
