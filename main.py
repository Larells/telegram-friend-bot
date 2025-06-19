import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv
import openai
from gtts import gTTS
from io import BytesIO
import speech_recognition as sr
from pydub import AudioSegment
import requests

# Загрузка переменных окружения
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")

# Настройка OpenAI
openai.api_key = OPENAI_API_KEY

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Простая память на время работы бота
memory = {}

# Кнопки
keyboard = ReplyKeyboardMarkup([["💬 Поговори", "🎨 Картинка"], ["🎤 Скажи голосом"]], resize_keyboard=True)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Я твой ИИ-друг 🤖", reply_markup=keyboard)

def handle_text(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text
    memory.setdefault(user_id, []).append(text)
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "Ты дружелюбный собеседник."},
        *[{"role": "user", "content": m} for m in memory[user_id][-5:]]
    ])
    answer = response.choices[0].message.content
    update.message.reply_text(answer)

def generate_image(update: Update, context: CallbackContext):
    update.message.reply_text("Напиши, что нарисовать!")

def handle_voice(update: Update, context: CallbackContext):
    file = update.message.voice.get_file()
    file_path = file.download()
    audio = AudioSegment.from_ogg(file_path)
    wav_path = file_path + ".wav"
    audio.export(wav_path, format="wav")
    r = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = r.record(source)
        try:
            text = r.recognize_google(audio_data, language="ru-RU")
            update.message.reply_text(f"Ты сказал: {text}")
            update.message.text = text
            handle_text(update, context)
        except sr.UnknownValueError:
            update.message.reply_text("Не понял, попробуй ещё раз.")

def say_with_voice(update: Update, context: CallbackContext):
    tts = gTTS(text="Я рад с тобой говорить!", lang="ru")
    bio = BytesIO()
    tts.write_to_fp(bio)
    bio.seek(0)
    update.message.reply_voice(voice=bio)

def main():
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.regex("🎨 Картинка"), generate_image))
    dp.add_handler(MessageHandler(Filters.regex("🎤 Скажи голосом"), say_with_voice))
    dp.add_handler(MessageHandler(Filters.voice, handle_voice))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
