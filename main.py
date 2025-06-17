import os
import logging
import telebot
from telebot import types
import openai

# Настройки
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

# Логирование
logging.basicConfig(level=logging.INFO)

# Команда /start
@bot.message_handler(commands=["start"])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💬 Поболтать", "🧠 Задать вопрос", "🎲 Анекдот")
    bot.send_message(message.chat.id, "Привет! Я твой ИИ-друг 😊", reply_markup=markup)

# Основной обработчик
@bot.message_handler(func=lambda message: True)
def handle_all(message):
    if message.text == "🎲 Анекдот":
        bot.send_message(message.chat.id, "Почему утка смеётся? Потому что у неё кря-кря-кризис! 😂")
    elif message.text == "💬 Поболтать" or message.text == "🧠 Задать вопрос":
        bot.send_message(message.chat.id, "Напиши что-нибудь, и я отвечу!")
    else:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message.text}]
            )
            reply = response.choices[0].message.content.strip()
            bot.send_message(message.chat.id, reply)
        except Exception as e:
            bot.send_message(message.chat.id, "Произошла ошибка. Попробуй позже.")

bot.polling()
