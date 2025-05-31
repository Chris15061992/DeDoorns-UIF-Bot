import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters import Text
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = 5105714334  # @TheMemeMinister Telegram ID

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Language Selection Keyboard
language_kb = ReplyKeyboardMarkup(resize_keyboard=True)
language_kb.add(KeyboardButton("🇿🇦 English"), KeyboardButton("🇿🇦 Afrikaans"), KeyboardButton("🇱🇸 Sesotho"))

# Payment Options
payment_kb = ReplyKeyboardMarkup(resize_keyboard=True)
payment_kb.add(
    KeyboardButton("R20 - Online Account Creation"),
    KeyboardButton("R40 - Account + Docs Prep"),
    KeyboardButton("R70 - Full Application Assistance")
)

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.reply("Welkom! Please choose your language:\nKies jou taal:", reply_markup=language_kb)

@dp.message_handler(lambda message: message.text in ["🇿🇦 English", "🇿🇦 Afrikaans", "🇱🇸 Sesotho"])
async def language_selected(message: types.Message):
    await message.reply("Please choose your assistance package:", reply_markup=payment_kb)

@dp.message_handler(Text(startswith="R20"))
async def handle_r20(message: types.Message):
    await handle_payment(message, 20, "Online Account Creation")

@dp.message_handler(Text(startswith="R40"))
async def handle_r40(message: types.Message):
    await handle_payment(message, 40, "Account Creation + Document Prep")

@dp.message_handler(Text(startswith="R70"))
async def handle_r70(message: types.Message):
    await handle_payment(message, 70, "Full Application Assistance")

async def handle_payment(message, amount, package):
    payment_instructions = (
        f"💳 To continue with **{package}**, please pay R{amount} using one of the following methods:\n\n"
        "📍 *Flash Voucher (1Voucher / OTT / Shoprite / PEP)*\n"
        "➡️ Send the voucher code here.\n\n"
        "🏦 *Capitec EFT or Paysharp:*\n"
        "`Account Number:` +27716362638\n\n"
        "📲 Or contact via WhatsApp after payment: wa.me/27716362638\n\n"
        "Once paid, reply with your *Full Name* and *Cell Number*."
    )
    await message.reply(payment_instructions, parse_mode="Markdown")

@dp.message_handler()
async def collect_user_info(message: types.Message):
    full_name = message.text.strip()
    user_id = message.from_user.id
    phone_number = message.from_user.username or "No username"

    notify_admin = (
        f"📥 New Claim Submission\n\n"
        f"👤 Name: {full_name}\n"
        f"📞 Telegram ID: {user_id}\n"
        f"🔗 Telegram: @{message.from_user.username or 'N/A'}\n"
        f"💬 Preferred WhatsApp: +{full_name.split()[-1] if full_name[-1].isdigit() else 'Number not provided'}"
    )

    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=notify_admin)
    await message.reply("✅ Thank you. We will verify your payment and get back to you shortly via WhatsApp or Telegram.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
