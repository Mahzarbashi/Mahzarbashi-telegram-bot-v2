import os
import asyncio
from telegram.ext import Application

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN در محیط Render تعریف نشده!")

WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"

async def main():
    app = Application.builder().token(TOKEN).build()
    await app.initialize()
    await app.bot.set_webhook(url=WEBHOOK_URL)
    print(f"✅ Webhook set to: {WEBHOOK_URL}")
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
