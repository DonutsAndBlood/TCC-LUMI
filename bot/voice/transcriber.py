from typing import Any, TypedDict

import numpy as np
from whisper import Whisper

from bot.whisper import Model


class TranscribeResult(TypedDict):
    text: str
    segments: list[Any]
    language: str


def transcribe_audio(array: np.ndarray[Any, Any]) -> str:
    # TODO Create decoding options
    model: Whisper = Model()
    result: TranscribeResult = model.transcribe(
        audio=array,
        verbose=True,
        language="pt",
    )
    return result["text"]
