
import logging
import json
import os
import openai
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from gtts import gTTS
import tempfile
import speech_recognition as sr

# Загрузка конфигурации
with open("config.json", "r") as f:
    config = json.load(f)

TELEGRAM_TOKEN = config["telegram_token"]
OPENAI_API_KEY = config["openai_api_key"]
ADMIN_USERNAME = config["admin_username"]

openai.api_key = OPENAI_API_KEY
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

# Память чата
chat_memory = {}

# Кнопки
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(KeyboardButton("💬 Поговори со мной"), KeyboardButton("😂 Анекдот"))
main_kb.add(KeyboardButton("🎨 Сгенерируй изображение"), KeyboardButton("🗣️ Отправь голос"))

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer("Привет! Я твой бот-друг 🤗", reply_markup=main_kb)

@dp.message_handler(lambda message: message.text == "💬 Поговори со мной")
async def talk(msg: types.Message):
    await msg.answer("Напиши, о чём хочешь поговорить?")

@dp.message_handler(lambda message: message.text == "😂 Анекдот")
async def joke(msg: types.Message):
    with open("jokes.txt", "r", encoding="utf-8") as f:
        jokes = f.readlines()
    from random import choice
    await msg.answer(choice(jokes))

@dp.message_handler(lambda message: message.text == "🎨 Сгенерируй изображение")
async def generate_image(msg: types.Message):
    await msg.answer("Что нарисовать? Напиши описание.")

@dp.message_handler(lambda message: message.text == "🗣️ Отправь голос")
async def send_voice(msg: types.Message):
    text = "Привет! Это голос от бота-друга."
    tts = gTTS(text)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as fp:
        tts.save(fp.name)
        await msg.answer_voice(types.InputFile(fp.name))
    os.unlink(fp.name)

@dp.message_handler(content_types=types.ContentType.VOICE)
async def handle_voice(msg: types.Message):
    file_info = await bot.get_file(msg.voice.file_id)
    file_path = file_info.file_path
    file = await bot.download_file(file_path)
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f:
        f.write(file.read())
        f.flush()
        try:
            from pydub import AudioSegment
            sound = AudioSegment.from_ogg(f.name)
            wav_path = f.name + ".wav"
            sound.export(wav_path, format="wav")

            r = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio = r.record(source)
                text = r.recognize_google(audio, language="ru-RU")
                await msg.answer(f"Ты сказал: {text}")
                os.remove(wav_path)
        except Exception as e:
            await msg.answer(f"Ошибка распознавания: {e}")
        finally:
            os.remove(f.name)

@dp.message_handler()
async def gpt_chat(msg: types.Message):
    user_id = str(msg.from_user.id)
    if user_id not in chat_memory:
        chat_memory[user_id] = []
    chat_memory[user_id].append({"role": "user", "content": msg.text})

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=chat_memory[user_id][-10:]
    )
    answer = response.choices[0].message["content"]
    chat_memory[user_id].append({"role": "assistant", "content": answer})
    await msg.answer(answer)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
