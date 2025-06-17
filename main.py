import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import openai

BOT_NAME = "ТвойДруг 🤖"

openai.api_key = os.getenv("OPENAI_API_KEY")

logging.basicConfig(level=logging.INFO)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Как дела?"], ["Поддержи меня"], ["Пошути"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"Привет! Я {BOT_NAME}. Я рядом, если тебе тяжело ❤️", reply_markup=reply_markup
    )

# Ответ на сообщения
async def respond(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    if "пошути" in user_message.lower():
        prompt = "Расскажи добрую и короткую шутку"
    elif "поддерж" in user_message.lower():
        prompt = "Скажи что-то тёплое и ободряющее, будто ты настоящий друг"
    elif "как дела" in user_message.lower():
        prompt = "Спроси у человека, как у него дела, и пожелай что-то хорошее"
    else:
        prompt = f"Ты — добрый друг. Ответь на сообщение: {user_message}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response["choices"][0]["message"]["content"]
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("Что-то пошло не так 😢")

# Запуск бота
def main():
    token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond))
    print("Bot is polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
