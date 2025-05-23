import whisper


class Model:

    _instance: whisper.Whisper = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = whisper.load_model("turbo", in_memory=True)
        return cls._instance

    @classmethod
    def load_model(cls):
        if cls._instance is None:
            cls._instance = whisper.load_model("turbo", in_memory=True)
        return cls._instance
