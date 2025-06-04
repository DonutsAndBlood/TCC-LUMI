import logging

import whisper

MODEL = "turbo"


class Model(whisper.Whisper):  # type: ignore[misc] # (Cannot subclass because Whisper is untyped)
    """Singleton class to manage the Whisper model."""

    _instance: whisper.Whisper = None

    def __new__(cls) -> whisper.Whisper:
        """Create a new instance of the Whisper model if it doesn't exist."""
        if cls._instance is None:
            cls._instance = whisper.load_model(MODEL, in_memory=True)
        return cls._instance

    @classmethod
    def load_model(cls):
        """Load the Whisper model if not already loaded."""
        if cls._instance is None:
            cls._instance = whisper.load_model(MODEL, in_memory=True)
            logging.info("Whisper model '%s' loaded", MODEL)
        return cls._instance
