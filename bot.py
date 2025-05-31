import logging from aiogram import Bot, Dispatcher, types, executor from aiogram.types import ReplyKeyboardMarkup, KeyboardButton from aiogram.dispatcher.filters import Text import os from dotenv import load_dotenv

Load environment variables

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN") ADMIN_ID = 5105714334  # @TheMemeMinister Telegram numeric ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN) dp = Dispatcher(bot)

Keyboards

payment_kb = ReplyKeyboardMarkup(resize_keyboard=True) payment_kb.add("Pay R20 - Account Only", "Pay R40 - Account + Docs", "Pay R70 - Full Assistance")

main_kb = ReplyKeyboardMarkup(resize_keyboard=True) main_kb.add("Start UIF Claim", "Help via WhatsApp")

@dp.message_handler(commands=['start']) async def send_welcome(message: types.Message): await message.answer("👋 Welcome to the DeDoorns UIF Choppa Bot!\nPlease choose an option below:", reply_markup=main_kb)

@dp.message_handler(Text(equals="Help via WhatsApp")) async def whatsapp_info(message: types.Message): await message.answer("📲 For help via WhatsApp, contact: +27716362638")

@dp.message_handler(Text(equals="Start UIF Claim")) async def start_claim(message: types.Message): await message.answer("💳 Please select your payment option:", reply_markup=payment_kb)

@dp.message_handler(lambda message: message.text.startswith("Pay R")) async def handle_payment_selection(message: types.Message): option = message.text if "R20" in option: tier = "Account Creation Only" amount = "R20" elif "R40" in option: tier = "Account + Documents" amount = "R40" elif "R70" in option: tier = "Full Assistance" amount = "R70" else: await message.answer("❌ Invalid selection. Try again.") return

await message.answer(
    f"✅ You selected: {tier}\n💰 Please pay {amount} via one of the following methods:\n\n"
    "1️⃣ *Capitec Immediate EFT / PaySharp:*\nAccount Number: +27716362638\nBank: Capitec\n\n"
    "2️⃣ *Voucher Payment (Flash Supported):*\nUse one of the following voucher types: 1Voucher, OTT, PEP, Shoprite\n\n"
    "Once done, reply with your *Name*, *Surname*, *Telegram Number*, and *Voucher Code* if used."
)

@dp.message_handler(lambda message: len(message.text.split()) >= 3) async def collect_info(message: types.Message): text = message.text user = message.from_user info = f"📥 New UIF Claim Request\n\n" info += f"👤 Name & Surname: {text}\n" info += f"📱 Telegram Number: +{user.id}\n" info += f"🔗 Username: @{user.username}\n"

await bot.send_message(ADMIN_ID, info)
await message.answer("✅ Thank you. We’ve received your details and will process your request after verifying your payment. For urgent help, WhatsApp us at +27716362638")

if name == 'main': executor.start_polling(dp, skip_updates=True)

