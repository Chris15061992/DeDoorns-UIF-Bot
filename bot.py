import logging import os from aiogram import Bot, Dispatcher, types from aiogram.types import ReplyKeyboardMarkup, KeyboardButton from aiogram.dispatcher.webhook import SendMessage from aiogram.utils.executor import start_webhook from dotenv import load_dotenv

Load environment variables

load_dotenv()

Bot token and webhook settings

BOT_TOKEN = os.getenv("BOT_TOKEN") WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")  # Your domain name or public IP WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}" WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = '0.0.0.0' WEBAPP_PORT = int(os.getenv("PORT", default=3000))

Admin Telegram ID (do not expose this in public repos)

ADMIN_ID = int(os.getenv("ADMIN_ID"))

Initialize bot and dispatcher

bot = Bot(token=BOT_TOKEN) dp = Dispatcher(bot)

Set up logging

logging.basicConfig(level=logging.INFO)

Language-specific instructions

LANGUAGES = { "English": "Please enter your cellphone number:", "Afrikaans": "Voer asseblief jou selfoonnommer in:", "isiXhosa": "Nceda ngenisa inombolo yakho yefowuni:" }

Confirmation instructions

UPLOAD_INSTRUCTIONS = { "English": "Thank you. Please upload your proof of UIF claim (photo/screenshot).", "Afrikaans": "Dankie. Laai asseblief jou bewys van UIF-aanspraak op (foto/skermskoot).", "isiXhosa": "Enkosi. Nceda ulayishe ubungqina bokufaka isicelo se-UIF (ifoto/skrinshoti)." }

Notification message to admin

NOTIFY_ADMIN_MSG = { "English": "New UIF claim:", "Afrikaans": "Nuwe UIF-aanspraak:", "isiXhosa": "Ibango elitsha le-UIF:" }

Start command

@dp.message_handler(commands=["start"]) async def start_cmd(message: types.Message): language_keyboard = ReplyKeyboardMarkup( keyboard=[ [KeyboardButton(text="English")], [KeyboardButton(text="Afrikaans")], [KeyboardButton(text="isiXhosa")] ], resize_keyboard=True, one_time_keyboard=True ) await message.answer("Welcome! Please choose your language:\nWelkom! Kies asseblief jou taal:\nWamkelekile! Nceda ukhethe ulwimi lwakho:", reply_markup=language_keyboard)

Store user states in memory

user_language = {} user_phone = {}

Handle language selection

@dp.message_handler(lambda message: message.text in LANGUAGES) async def handle_language(message: types.Message): user_language[message.from_user.id] = message.text await message.answer(LANGUAGES[message.text], reply_markup=types.ReplyKeyboardRemove())

Handle phone number

@dp.message_handler(lambda message: message.text.isdigit()) async def handle_phone(message: types.Message): lang = user_language.get(message.from_user.id, "English") user_phone[message.from_user.id] = message.text await message.answer(UPLOAD_INSTRUCTIONS[lang])

Handle image upload

@dp.message_handler(content_types=[types.ContentType.PHOTO]) async def handle_photo(message: types.Message): lang = user_language.get(message.from_user.id, "English") phone = user_phone.get(message.from_user.id, "[No number provided]")

# Send confirmation to admin privately
photo = message.photo[-1]
caption = f"{NOTIFY_ADMIN_MSG[lang]}\nPhone: {phone}\nUser: @{message.from_user.username or message.from_user.id}"
await bot.send_photo(chat_id=ADMIN_ID, photo=photo.file_id, caption=caption)
await message.answer("✅ Submission received. Thank you!")

Webhook startup

async def on_startup(dp): await bot.set_webhook(WEBHOOK_URL)

Webhook shutdown

async def on_shutdown(dp): logging.warning("Shutting down..") await bot.delete_webhook() logging.warning("Bye!")

if name == 'main': start_webhook( dispatcher=dp, webhook_path=WEBHOOK_PATH, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True, host=WEBAPP_HOST, port=WEBAPP_PORT, )

