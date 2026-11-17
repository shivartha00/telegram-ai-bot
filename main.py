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
  try:
    # সরাসরি উপলব্ধ মডেলগুলোর তালিকা থেকে প্রথমটি অটোমেটিক বেছে নেবে
    available_models = [
        m.name
        for m in client.models.list()
        if "generateContent" in m.supported_generation_methods
    ]

    target_model = (
        available_models[0]
        if available_models
        else "models/gemini-1.5-flash"
    )

    response = client.models.generate_content(
        model=target_model, contents=message.text
    )
    bot.reply_to(message, response.text)
  except Exception as e:
    bot.reply_to(message, f"Error: {str(e)}")


if __name__ == "__main__":
  t = threading.Thread(target=run_flask)
  t.start()

  print("Telegram AI Bot chalu hoye geche...")
  bot.polling()
