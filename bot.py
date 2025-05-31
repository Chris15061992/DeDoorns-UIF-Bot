import logging from aiogram import Bot, Dispatcher, types, executor from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile from aiogram.dispatcher.filters import Text from aiogram.contrib.middlewares.logging import LoggingMiddleware import os

API_TOKEN = os.getenv("BOT_TOKEN")  # Load from environment ADMIN_ID = 5105714334  # @TheMemeMinister

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN) dp = Dispatcher(bot) dp.middleware.setup(LoggingMiddleware())

Multilingual welcome

WELCOME_TEXT = { 'en': "👋 Welcome to the UIF Assistant Bot! Please pay a R50 once-off fee for full help.", 'af': "👋 Welkom by die UIF Assistent Bot! Betaal asseblief 'n eenmalige fooi van R50.", 'xh': "👋 Wamkelekile kwi-UIF Uncedo Bot! Nceda uhlawule imali eyi-R50 kube kanye.", 'zu': "👋 Siyakwamukela ku-UIF Usizo Bot! Sicela ukhokhe u-R50 kube kanye.", 'st': "👋 Rea u amohela ho UIF Bot ea Thuso! Ka kopo lefe R50 hang feela." }

Basic payment instruction

PAYMENT_INSTRUCTIONS = ( "\U0001F4B3 UIF Assistant Fee – R50 (Once-Off)\n\n" "You can pay using the following methods:\n" "✅ 1Voucher\n✅ OTT Voucher\n✅ Shoprite / Checkers\n✅ PEP Money Transfer\n✅ Capitec PaySharp or Immediate EFT\n\n" "\U0001F4E4 Send the voucher code here\n" "OR\n" "\U0001F4F8 Upload a clear photo of your voucher or payment confirmation\n\n" "Your payment will be verified and assistance begins after confirmation.\n\n" "\U0001F4B5 Capitec Account for EFT: +27 71 636 2638\n" "\U0001F4DE WhatsApp Help: +27 71 636 2638" )

Markup

lang_keyboard = ReplyKeyboardMarkup(resize_keyboard=True) lang_keyboard.add(KeyboardButton("English"), KeyboardButton("Afrikaans")) lang_keyboard.add(KeyboardButton("isiXhosa"), KeyboardButton("isiZulu")) lang_keyboard.add(KeyboardButton("Sesotho"))

@dp.message_handler(commands=['start']) async def send_welcome(message: types.Message): await message.reply("🌐 Please choose your language:", reply_markup=lang_keyboard)

@dp.message_handler(lambda m: m.text in ["English", "Afrikaans", "isiXhosa", "isiZulu", "Sesotho"]) async def language_chosen(message: types.Message): lang_map = { "English": 'en', "Afrikaans": 'af', "isiXhosa": 'xh', "isiZulu": 'zu', "Sesotho": 'st' } code = lang_map[message.text] await message.answer(WELCOME_TEXT[code]) await message.answer(PAYMENT_INSTRUCTIONS, parse_mode="Markdown")

@dp.message_handler(content_types=['text', 'photo']) async def handle_payment_submission(message: types.Message): user = message.from_user text = f"\n👤 New Payment Submission\n" text += f"Name: {user.full_name}\nPhone: {user.id}\n" if message.text: text += f"Voucher Code or Reference: {message.text}" await bot.send_message(ADMIN_ID, text, parse_mode='Markdown')

if message.photo:
    file_id = message.photo[-1].file_id
    await bot.send_photo(ADMIN_ID, file_id, caption=f"Voucher/payment image from {user.full_name} ({user.id})")

await message.answer("⏳ Thank you. Your voucher or payment has been received and is being verified.")

Optional: Admin command to mark user as paid

@dp.message_handler(commands=['mark_paid']) async def mark_user_paid(message: types.Message): if message.from_user.id != ADMIN_ID: return await message.reply("Unauthorized") try: parts = message.text.split() if len(parts) < 2: return await message.reply("Usage: /mark_paid <telegram_user_id>") user_id = int(parts[1]) await bot.send_message(user_id, "✅ Your payment has been confirmed. Thank you! You will now receive full UIF assistance.") await message.reply("User notified.") except Exception as e: await message.reply(f"Error: {e}")

if name == 'main': executor.start_polling(dp, skip_updates=True)

