import os
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from telegram.constants import ParseMode

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=4, use_context=True)

# ==================== LANGUAGES ====================

languages = {
    'en': "English",
    'xh': "isiXhosa",
    'zu': "isiZulu",
    'st': "Sesotho",
    'af': "Afrikaans"
}

# ==================== START ====================

def start(update, context):
    keyboard = [[InlineKeyboardButton(lang, callback_data=f"lang_{code}")]
                for code, lang in languages.items()]
    update.message.reply_text("Please choose your language / Khetha ulwimi lwakho:", reply_markup=InlineKeyboardMarkup(keyboard))

def handle_language(update, context):
    query = update.callback_query
    query.answer()
    lang_code = query.data.split("_")[1]
    context.user_data["lang"] = lang_code

    query.message.reply_text(
        "Please choose your UIF help option:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("R20 - Account Creation", callback_data="help_20")],
            [InlineKeyboardButton("R40 - Account + Docs", callback_data="help_40")],
            [InlineKeyboardButton("R70 - Full Assistance", callback_data="help_70")]
        ])
    )

# ==================== HELP OPTION ====================

def handle_help_option(update, context):
    query = update.callback_query
    query.answer()
    selection = query.data.split("_")[1]
    context.user_data["payment_option"] = selection

    descriptions = {
        "20": "You selected *R20* - Account creation assistance.",
        "40": "You selected *R40* - Account + Document preparation.",
        "70": "You selected *R70* - Full UIF assistance."
    }

    query.message.reply_text(
        f"{descriptions[selection]}\n\nNow choose your payment method:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("1Voucher / OTT", callback_data="pay_voucher")],
            [InlineKeyboardButton("EFT / Bank Transfer", callback_data="pay_eft")]
        ])
    )

# ==================== PAYMENT OPTIONS ====================

def handle_payment(update, context):
    query = update.callback_query
    query.answer()
    method = query.data.split("_")[1]
    context.user_data["pay_method"] = method

    if method == "voucher":
        query.message.reply_text(
            "Please type your 16-digit voucher number or upload screenshot of your voucher here.\n\nBuy a 1Voucher or OTT at any retail store."
        )
    elif method == "eft":
        query.message.reply_text(
            "*Please make an EFT payment to the details below:*\n\n"
            "🏦 Bank: Capitec\n"
            "📌 Account Number: *1363559271*\n\n"
            "After payment, send a screenshot *with your full name, ID number, and cellphone number* for confirmation.",
            parse_mode=ParseMode.MARKDOWN
        )

# ==================== PROOF HANDLING ====================

def handle_proof(update, context):
    user = update.message.from_user
    context.user_data["proof"] = True

    msg = f"""
📥 *New UIF Claim Submission*

👤 Name: {user.full_name}
🆔 Telegram ID: `{user.id}`
📞 Phone: {user.username or 'N/A'}

💳 Payment Option: R{context.user_data.get("payment_option", 'N/A')}
💰 Method: {context.user_data.get("pay_method", 'N/A')}
"""

    if update.message.photo:
        photo_file = update.message.photo[-1].file_id
        bot.send_photo(chat_id=ADMIN_ID, photo=photo_file, caption=msg, parse_mode=ParseMode.MARKDOWN)
    else:
        msg += f"\n📝 Text: {update.message.text}"
        bot.send_message(chat_id=ADMIN_ID, text=msg, parse_mode=ParseMode.MARKDOWN)

    update.message.reply_text(
        "✅ Thank you! We’ve received your payment. We’ll be in touch soon.\n\nIf you need urgent help, use the buttons below 👇",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📞 WhatsApp Help", url="https://wa.me/27716362638")],
            [InlineKeyboardButton("📩 Message Admin", url="https://t.me/TheMemeMinister")]
        ])
    )

# ==================== DISPATCHERS ====================

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(handle_language, pattern="^lang_"))
dispatcher.add_handler(CallbackQueryHandler(handle_help_option, pattern="^help_"))
dispatcher.add_handler(CallbackQueryHandler(handle_payment, pattern="^pay_"))
dispatcher.add_handler(MessageHandler(Filters.text | Filters.photo, handle_proof))

# ==================== FLASK ROUTE ====================

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/")
def index():
    return "DeDoorns UIF Bot is running."

# ==================== MAIN ====================

if __name__ == "__main__":
    app.run(port=5000)
