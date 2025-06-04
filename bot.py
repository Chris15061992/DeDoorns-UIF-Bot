import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiogram.dispatcher.webhook import SendMessage
from aiogram.utils.executor import start_webhook
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

WEBHOOK_HOST = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", default=8000))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

languages = {
    "English": {
        "welcome": "Welcome to De Doorns UIF Choppa Bot 👨🏽‍🌾",
        "select_package": "Please choose your assistance package:",
        "options": [
            "R20 - Account creation only",
            "R40 - Account creation + document prep",
            "R70 - Full assistance with application"
        ],
        "payment_instruction": "Pay via EFT or 1Voucher/OTT and upload proof or enter your 16-digit code below.",
        "eft_details": "Capitec Account: 1363559271",
        "proof_prompt": "Please upload your proof of payment or voucher code.",
        "thanks": "✅ Thank you! We’ll be in touch soon. Need urgent help?",
        "urgent_help": "WhatsApp Support",
    },
    "Afrikaans": {
        "welcome": "Welkom by De Doorns UIF Choppa Bot 👨🏽‍🌾",
        "select_package": "Kies asseblief jou hulppakket:",
        "options": [
            "R20 - Rekening skepping slegs",
            "R40 - Rekening skepping + dokumente",
            "R70 - Volledige hulp met aansoek"
        ],
        "payment_instruction": "Betaal via EFT of 1Voucher/OTT en laai bewys of 16-syfer kode op.",
        "eft_details": "Capitec Rekening: 1363559271",
        "proof_prompt": "Laai asseblief jou betalingsbewys of voucher kode op.",
        "thanks": "✅ Dankie! Ons sal binnekort kontak maak. Dringende hulp nodig?",
        "urgent_help": "WhatsApp Ondersteuning",
    },
    "Xhosa": {
        "welcome": "Wamkelekile kwi De Doorns UIF Choppa Bot 👨🏽‍🌾",
        "select_package": "Nceda ukhethe ipakethe yakho yoncedo:",
        "options": [
            "R20 - Ukwenza i-akhawunti kuphela",
            "R40 - Iakhawunti + amaxwebhu",
            "R70 - Uncedo olupheleleyo lwesicelo"
        ],
        "payment_instruction": "Hlawula nge-EFT okanye 1Voucher/OTT kwaye ungenise ubungqina okanye ikhowudi ye-16-digit.",
        "eft_details": "iCapitec iAkhawunti: 1363559271",
        "proof_prompt": "Nceda ngenisa ubungqina bokuhlawula okanye ikhowudi yeVoucher.",
        "thanks": "✅ Enkosi! Siza kuqhagamshelana kungekudala. Uyafuna uncedo olukhawulezileyo?",
        "urgent_help": "Inkxaso kaWhatsApp",
    }
}

user_language = {}

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("English"), KeyboardButton("Afrikaans"), KeyboardButton("Xhosa"))
    await message.answer("🌍 Please select your language / Kies jou taal / Khetha ulwimi lwakho:", reply_markup=keyboard)

@dp.message_handler(lambda msg: msg.text in languages.keys())
async def language_selected(message: types.Message):
    lang = message.text
    user_language[message.from_user.id] = lang
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for option in languages[lang]["options"]:
        kb.add(KeyboardButton(option))
    await message.answer(languages[lang]["welcome"])
    await message.answer(languages[lang]["select_package"], reply_markup=kb)

@dp.message_handler(lambda msg: any(msg.text.startswith(opt[:3]) for lang in languages.values() for opt in lang["options"]))
async def option_selected(message: types.Message):
    lang = user_language.get(message.from_user.id, "English")
    await message.answer(languages[lang]["payment_instruction"])
    await message.answer(f"💳 {languages[lang]['eft_details']}")
    await message.answer(languages[lang]["proof_prompt"])

@dp.message_handler(content_types=["photo", "document", "text"])
async def handle_proof(message: types.Message):
    lang = user_language.get(message.from_user.id, "English")

    full_name = message.from_user.full_name
    phone = message.contact.phone_number if message.contact else message.from_user.username or "N/A"
    text = message.text if message.text else "Voucher or unknown text"

    caption = f"🧾 New Payment Submission\n\n👤 Name: {full_name}\n📱 Contact: @{message.from_user.username}\n🪪 Text: {text}"

    if message.photo:
        await bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption=caption)
    elif message.document:
        await bot.send_document(chat_id=ADMIN_ID, document=message.document.file_id, caption=caption)
    else:
        await bot.send_message(chat_id=ADMIN_ID, text=caption)

    # Thank You + WhatsApp
    thank = languages[lang]["thanks"]
    wa_url = "https://wa.me/27716362638"
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(languages[lang]["urgent_help"], url=wa_url))
    await message.answer(thank, reply_markup=kb)

# Webhook startup
async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dp):
    await bot.delete_webhook()

if __name__ == "__main__":
    from aiogram import executor
    executor.start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
)
