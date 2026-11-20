import os
import threading
import time
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
  url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
  headers = {"Content-Type": "application/json"}
  payload = {"contents": [{"parts": [{"text": message.text}]}]}

  # ৫১৩ সার্ভার ওভারলোড এরর এড়াতে ৩ বার ট্রাই করবে
  for attempt in range(3):
    try:
      response = requests.post(url, json=payload, headers=headers)
      res_data = response.json()

      if "candidates" in res_data:
        reply_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
        bot.reply_to(message, reply_text)
        return
      elif (
          "error" in res_data
          and res_data["error"].get("code") == 503
          and attempt < 2
      ):
        time.sleep(2)
        continue
      else:
        bot.reply_to(message, f"API Error: {res_data}")
        return
    except Exception as e:
      if attempt == 2:
        bot.reply_to(message, f"Error: {str(e)}")
      time.sleep(2)


if __name__ == "__main__":
  t = threading.Thread(target=run_flask)
  t.start()
  bot.polling()

