import logging
import os
from aiogram import Bot, Dispatcher, types, executor
from openai import OpenAI
from utils import get_reply, generate_image, transcribe_voice, speak_text

API_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "@admin")
USE_TTS = os.getenv("USE_TTS", "true").lower() == "true"
USE_STT = os.getenv("USE_STT", "true").lower() == "true"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
openai = OpenAI(api_key=OPENAI_API_KEY)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply("Привет! Я твой друг-бот. Напиши мне что-нибудь ❤️")

@dp.message_handler(commands=["joke"])
async def joke(message: types.Message):
    await message.reply("Вот анекдот:
Почему компьютер устал? Потому что у него слишком много задач!")

@dp.message_handler(content_types=types.ContentType.VOICE)
async def handle_voice(message: types.Message):
    if not USE_STT:
        await message.reply("Распознавание голосовых отключено.")
        return
    file = await bot.get_file(message.voice.file_id)
    path = file.file_path
    file_data = await bot.download_file(path)
    text = transcribe_voice(file_data)
    response = get_reply(text)
    if USE_TTS:
        audio = speak_text(response)
        await message.reply_voice(audio)
    else:
        await message.reply(response)

@dp.message_handler()
async def chat(message: types.Message):
    response = get_reply(message.text)
    if USE_TTS:
        audio = speak_text(response)
        await message.reply_voice(audio)
    else:
        await message.reply(response)

if __name__ == "__main__":
    executor.start_polling(dp)
