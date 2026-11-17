import os
import threading
from flask import Flask
from google import genai
import telebot

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

app = Flask(__name__)


@app.route("/")
def home():
  return "Telegram AI Bot is running successfully!"


def run_flask():
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
  models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash"]
  success = False
  response_text = ""

  for m in models_to_try:
    try:
      response = client.models.generate_content(
          model=m, contents=message.text
      )
      response_text = response.text
      success = True
      break
    except Exception as e:
      continue

  if success:
    bot.reply_to(message, response_text)
  else:
    bot.reply_to(
        message, "Ekhon server-e beshi load ache. Ektu pore abar try korun!"
    )


if __name__ == "__main__":
  t = threading.Thread(target=run_flask)
  t.start()

  print("Telegram AI Bot chalu hoye geche...")
  bot.polling()
