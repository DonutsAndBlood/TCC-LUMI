from io import BytesIO
from typing import Any

import librosa
import noisereduce
import numpy as np
from scipy.io import wavfile


def read_audio_io(io: BytesIO) -> tuple[int, np.ndarray[Any, Any]]:
    rate, data = wavfile.read(io)
    data = np.reshape(data, (2, -1))
    return (rate, data)


def reduce_noise(io: BytesIO):
    sample_rate, data = read_audio_io(io)
    denoised = noisereduce.reduce_noise(y=data, sr=sample_rate)
    return denoised


def load_audio_ndarray(io: bytes) -> np.ndarray[Any, Any]:
    try:
        data, _sample_rate = librosa.load(io, mono=True, sr=16000)
        return data
    except Exception as e:
        print(f"Error reading audio: {e}")
        raise ValueError("Invalid audio data") from e
