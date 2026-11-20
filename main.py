import os
import threading
from flask import Flask
import requests
import telebot

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)


@app.route("/")
def home():
  return "Double Engine Bot is running!"


def run_flask():
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)


def ask_gemini(model_name, text):
  url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
  headers = {"Content-Type": "application/json"}
  payload = {"contents": [{"parts": [{"text": text}]}]}
  res = requests.post(url, json=payload, headers=headers, timeout=15)
  data = res.json()
  if "candidates" in data:
    return data["candidates"][0]["content"]["parts"][0]["text"]
  return None


def ask_groq(text):
  url = "https://api.groq.com/openai/v1/chat/completions"
  headers = {
      "Authorization": f"Bearer {GROQ_API_KEY}",
      "Content-Type": "application/json",
  }
  payload = {
      "model": "openai/gpt-oss-20b",
      "messages": [{"role": "user", "content": text}],
  }
  res = requests.post(url, json=payload, headers=headers, timeout=15)
  data = res.json()
  if "choices" in data:
    return data["choices"][0]["message"]["content"]
  return f"Groq Error: {data}"


@bot.message_handler(func=lambda message: True)
def handle_message(message):
  user_text = message.text

  # First Engine: Gemini Flash + Lite
  for model in ["gemini-3.8-flash", "gemini-3.8-flash-lite"]:
    try:
      reply = ask_gemini(model, user_text)
      if reply:
        bot.reply_to(message, reply)
        return
    except Exception:
      continue

  # Second Engine: Groq API
  try:
    reply = ask_groq(user_text)
    if reply:
      bot.reply_to(message, reply)
      return
  except Exception as e:
    bot.reply_to(message, f"Groq Exception: {e}")
    return

  bot.reply_to(message, "Sob engine ekhon busy ache. Ektu pore abar try korun.")


if __name__ == "__main__":
  t = threading.Thread(target=run_flask)
  t.start()
  bot.polling()
