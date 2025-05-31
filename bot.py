import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# States for conversation
(START, COLLECT_NUMBER, COLLECT_LOCATION, THANK_YOU) = range(4)

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "👋 Welcome to *DeDoorns UIF Choppa Bot*!\n\n"
        "We help farm workers quickly register and receive UIF assistance.\n\n"
        "📱 Let's begin with your cellphone number:",
        parse_mode="Markdown",
    )
    return COLLECT_NUMBER

# Collect cellphone number
async def collect_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_number = update.message.text.strip()
    context.user_data["cell"] = user_number

    await update.message.reply_text(
        "📍 Please enter your last *farming location* (e.g., De Doorns, Worcester):",
        parse_mode="Markdown",
    )
    return COLLECT_LOCATION

# Collect location
async def collect_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    location = update.message.text.strip()
    context.user_data["location"] = location

    # Save to Google Sheet or database later here

    await update.message.reply_text(
        "✅ Thank you! Your information has been received.\n\n"
        "We will keep you updated as support becomes available. 💬",
    )
    return ConversationHandler.END

# Cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ Cancelled. Send /start to try again.")
    return ConversationHandler.END

# Main app
if __name__ == "__main__":
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            COLLECT_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_number)],
            COLLECT_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_location)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("🤖 Bot is running...")
    app.run_polling()
