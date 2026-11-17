import os
import threading
from flask import Flask
from google import genai
import telebot

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

# Render-এর পোর্ট রিকোয়ারমেন্ট পূরণের জন্য ছোট একটি ফ্লাস্ক অ্যাপ
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
    response = client.models.generate_content(
        model="gemini-3.8-flash", contents=message.text
    )
    bot.reply_to(message, response.text)
  except Exception as e:
    bot.reply_to(message, f"Error: {str(e)}")


if __name__ == "__main__":
  # ফ্লাস্ক সার্ভার ব্যাকগ্রাউন্ডে রান করবে
  t = threading.Thread(target=run_flask)
  t.start()

  print("Telegram AI Bot chalu hoye geche...")
  bot.polling()

