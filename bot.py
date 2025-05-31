import logging
import os
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters import Text
from aiogram.contrib.middlewares.logging import LoggingMiddleware

# Bot token and admin ID (replace with your actual bot token and Telegram user ID)
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5105714334  # @TheMemeMinister

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Keyboard for contact option
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(
    KeyboardButton("Submit UIF Claim 📄"),
    KeyboardButton("Pay Assistant Fee 💳")
)
keyboard.add(
    KeyboardButton("Get Help via WhatsApp 📱")
)

# Welcome message
WELCOME_MESSAGE = """\
🇿🇦 *Welcome to the De Doorns UIF Assistant Bot!*

This bot helps farm workers apply for UIF and prepare all needed documents.

Choose an option below to begin:

💡 *UIF Account Creation Only* — R20  
📄 *Account + Document Help* — R40  
🧾 *Full Assistance (Account + Docs + Application)* — R70

For WhatsApp help, message:  
📱 *+27 71 636 2638*

_Created for farm workers, by farm workers._
"""

# Updated payment tiers
PAYMENT_INSTRUCTIONS = """\
💳 *Payment Options:*

🔹 *R20* — *UIF Account Creation Only*  
🔹 *R40* — *Account + Document Gathering*  
🔹 *R70* — *Full UIF Assistance* (account + docs + application)

📌 *Voucher Methods Accepted:*
- 1Voucher  
- OTT Voucher  
- Shoprite/Checkers  
- PEP Money Transfer  

🎯 Send voucher PIN or proof to WhatsApp: *+27 71 636 2638*

📌 *EFT or PaySharp (Capitec):*
- Account Number (Cell): *+27 71 636 2638*  
- Bank: Capitec  
- Recipient: *Payment Assessor*

Once payment is received, we begin your process.
"""

# WhatsApp help message
WHATSAPP_HELP = """\
📱 For WhatsApp assistance:

Send your *Name*, *Surname*, and *Cell Number* to:

👉 *+27 71 636 2638*

We will assist you manually via WhatsApp after verifying your payment.

💬 Payment still applies before any support is provided.
"""

# /start handler
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer(WELCOME_MESSAGE, parse_mode="Markdown", reply_markup=keyboard)

# Claim process handler
@dp.message_handler(Text(equals="Submit UIF Claim 📄"))
async def handle_claim(message: types.Message):
    await message.reply("Please enter your *Full Name* and *Cell Number* (same as your Telegram number).", parse_mode="Markdown")
    await bot.send_message(
        ADMIN_ID,
        f"📝 New claimant started process:\nFrom: {message.from_user.full_name}\nTelegram ID: {message.from_user.id}"
    )

# Payment info handler
@dp.message_handler(Text(equals="Pay Assistant Fee 💳"))
async def handle_payment(message: types.Message):
    await message.reply(PAYMENT_INSTRUCTIONS, parse_mode="Markdown")

# WhatsApp help handler
@dp.message_handler(Text(equals="Get Help via WhatsApp 📱"))
async def handle_whatsapp(message: types.Message):
    await message.reply(WHATSAPP_HELP, parse_mode="Markdown")

# Default fallback
@dp.message_handler()
async def default_response(message: types.Message):
    await message.reply("Please use the buttons below to choose an option.", reply_markup=keyboard)

# Main entry point
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
