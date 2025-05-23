import io
import noisereduce


def reduce_noise(file: io.BytesIO, sample_rate: int):
    denoised = noisereduce.reduce_noise(y=file, sr=sample_rate)
    return denoised
