import logging
import os
from aiogram import Bot, Dispatcher, types, executor
from config import TELEGRAM_TOKEN, ADMIN_USERNAMES
from memory import Memory
from dalle import generate_image
from voice import speech_to_text, text_to_speech
from buttons import get_keyboard
import openai

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

memory = Memory()

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer("Привет, я твой ИИ-друг! ❤️", reply_markup=get_keyboard())

@dp.message_handler(commands=["admin"])
async def admin_cmd(msg: types.Message):
    if msg.from_user.username in ADMIN_USERNAMES:
        await msg.answer("Админ-команда выполнена.")
    else:
        await msg.answer("У тебя нет прав.")

@dp.message_handler(content_types=types.ContentType.VOICE)
async def handle_voice(msg: types.Message):
    voice_file = await msg.voice.get_file()
    file_path = f"voice.ogg"
    await voice_file.download(destination_file=file_path)

    text = speech_to_text(file_path)
    memory.add(msg.from_user.id, "user", text)
    await msg.answer(f"Ты сказал: {text}")
    response = memory.chat(msg.from_user.id)
    audio_path = text_to_speech(response)
    await bot.send_voice(msg.chat.id, open(audio_path, "rb"))

@dp.message_handler(lambda m: m.text == "Сгенерировать картинку")
async def handle_image_gen(msg: types.Message):
    await msg.answer("Напиши описание картинки 👇")

@dp.message_handler()
async def chat(msg: types.Message):
    user_id = msg.from_user.id
    memory.add(user_id, "user", msg.text)

    if msg.text.startswith("Картинка:"):
        prompt = msg.text.split("Картинка:", 1)[1].strip()
        image_url = generate_image(prompt)
        await msg.answer_photo(photo=image_url)
        return

    reply = memory.chat(user_id)
    await msg.answer(reply, reply_markup=get_keyboard())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)