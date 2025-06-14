import whisper

MODEL = "turbo"


class Model(whisper.Whisper):  # type: ignore[misc]

    _instance: whisper.Whisper = None

    def __new__(cls) -> whisper.Whisper:
        if cls._instance is None:
            cls._instance = whisper.load_model(MODEL, in_memory=True)
            print(f"Whisper model '{MODEL}' loaded")
        return cls._instance

    @classmethod
    def load_model(cls):
        if cls._instance is None:
            cls._instance = whisper.load_model(MODEL, in_memory=True)
            print(f"Whisper model '{MODEL}' loaded")
        return cls._instance
