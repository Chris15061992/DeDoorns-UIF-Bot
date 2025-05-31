from flask import Flask, request
import telegram
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def receive_update():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    text = update.message.text
    bot.send_message(chat_id=chat_id, text="👋 Hello! You said: " + text)
    return "ok"

@app.route("/")
def index():
    return "Bot is alive!"