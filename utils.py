from openai import OpenAI
import io
from gtts import gTTS
from pydub import AudioSegment
import speech_recognition as sr

openai = OpenAI()

def get_reply(text):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": text}]
    )
    return response.choices[0].message.content.strip()

def generate_image(prompt):
    response = openai.images.generate(
        prompt=prompt,
        n=1,
        size="512x512"
    )
    return response.data[0].url

def transcribe_voice(file_data):
    recognizer = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(file_data.read())) as source:
        audio = recognizer.record(source)
    return recognizer.recognize_google(audio, language="ru-RU")

def speak_text(text):
    tts = gTTS(text, lang="ru")
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp
