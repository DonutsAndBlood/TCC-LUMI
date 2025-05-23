import io
import speech_recognition as sr
from whisper import Whisper
from bot.whisper import Model


def transcribe_audio(file: io.BytesIO):
    model: Whisper = Model()
    result = model.transcribe(audio=file, verbose=True, language="pt")
    return result["text"]
