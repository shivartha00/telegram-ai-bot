import os
import threading
from flask import Flask
import requests
import telebot

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
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
    # সঠিক v1 ভার্সন এবং gemini-1.5-flash এন্ডপয়েন্ট
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": message.text}]}]}

    response = requests.post(url, json=payload, headers=headers)
    res_data = response.json()

    if "candidates" in res_data:
      reply_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
      bot.reply_to(message, reply_text)
    else:
      bot.reply_to(message, f"API Error: {res_data}")
  except Exception as e:
    bot.reply_to(message, f"Error: {str(e)}")


if __name__ == "__main__":
  t = threading.Thread(target=run_flask)
  t.start()

  print("Telegram AI Bot chalu hoye geche...")
  bot.polling()