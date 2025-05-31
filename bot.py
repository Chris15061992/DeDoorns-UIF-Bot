import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.webhook import SendMessage
from aiogram.utils.executor import start_webhook
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")  # keep this in your .env securely

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = f"/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.environ.get('PORT', 3000))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Supported languages
LANGUAGES = {
    "English": "en",
    "Afrikaans": "af",
    "isiXhosa": "xh"
}

user_language = {}

# Keyboards
language_kb = ReplyKeyboardMarkup(resize_keyboard=True)
language_kb.add(
    KeyboardButton("English"),
    KeyboardButton("Afrikaans"),
    KeyboardButton("isiXhosa")
)

def get_keyboard(lang):
    if lang == "en":
        return ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton("Claim UIF"),
            KeyboardButton("Submit Proof")
        )
    elif lang == "af":
        return ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton("Eis UIF"),
            KeyboardButton("Stuur Bewys")
        )
    elif lang == "xh":
        return ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton("Faka isicelo se-UIF"),
            KeyboardButton("Ngenisa Ubufakazi")
        )

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("Please select your language / Kies jou taal / Khetha ulwimi lwakho:", reply_markup=language_kb)

@dp.message_handler(lambda message: message.text in LANGUAGES)
async def set_language(message: types.Message):
    user_language[message.from_user.id] = LANGUAGES[message.text]
    lang = LANGUAGES[message.text]
    
    greetings = {
        "en": "Welcome to the De Doorns UIF Choppa Bot! Please select an option below:",
        "af": "Welkom by die De Doorns UIF Choppa Bot! Kies asseblief 'n opsie hieronder:",
        "xh": "Wamkelekile kwi-De Doorns UIF Choppa Bot! Nceda ukhethe ukhetho olungezantsi:"
    }
    await message.answer(greetings[lang], reply_markup=get_keyboard(lang))

@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_text(message: types.Message):
    lang = user_language.get(message.from_user.id, "en")
    text = message.text.lower()

    responses = {
        "en": {
            "claim uif": "Please enter your full name and last farm worked at.",
            "submit proof": "Please upload a photo or PDF as proof of payment."
        },
        "af": {
            "eis uif": "Voer asseblief jou volle naam en die laaste plaas waar jy gewerk het in.",
            "stuur bewys": "Laai asseblief 'n foto of PDF as bewys van betaling op."
        },
        "xh": {
            "faka isicelo se-uif": "Nceda ngenisa igama lakho elipheleleyo kunye nefama yokugqibela osebenze kuyo.",
            "ngenisa ubufakazi": "Nceda ulayishe ifoto okanye iPDF njengobungqina bentlawulo."
        }
    }

    for key in responses[lang]:
        if key in text:
            await message.answer(responses[lang][key])
            return

    fallback = {
        "en": "Sorry, I didn’t understand that. Please choose an option.",
        "af": "Jammer, ek het dit nie verstaan nie. Kies asseblief 'n opsie.",
        "xh": "Uxolo, andiqondanga. Nceda ukhethe ukhetho."
    }
    await message.answer(fallback[lang], reply_markup=get_keyboard(lang))

@dp.message_handler(content_types=types.ContentType.PHOTO)
@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_proof(message: types.Message):
    lang = user_language.get(message.from_user.id, "en")
    
    confirmations = {
        "en": "Thank you, your proof has been received.",
        "af": "Dankie, jou bewys is ontvang.",
        "xh": "Enkosi, ubungqina bakho bufunyenwe."
    }
    
    await message.answer(confirmations[lang])
    
    # Forward to admin
    try:
        await bot.send_message(ADMIN_ID, f"New proof from @{message.from_user.username or message.from_user.full_name}")
        if message.content_type == types.ContentType.PHOTO:
            await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption="UIF Proof")
        elif message.content_type == types.ContentType.DOCUMENT:
            await bot.send_document(ADMIN_ID, message.document.file_id, caption="UIF Proof")
    except Exception as e:
        logging.error(f"Failed to send proof to admin: {e}")

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dp):
    await bot.delete_webhook()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from aiogram import executor
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
