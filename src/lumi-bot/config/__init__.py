import logging
import os
from enum import StrEnum

from dotenv import find_dotenv, load_dotenv

env_path = find_dotenv()
if not env_path:
    raise FileNotFoundError(
        "No .env file found. Please create a .env file with the required environment variables."
    )


class Key(StrEnum):
    DISCORD_TOKEN = "DISCORD_TOKEN"
    API_URL = "API_URL"
    API_PORT = "API_PORT"
    ENV = "ENV"


class Defaults:
    DISCORD_TOKEN = None
    API_URL = "localhost"
    API_PORT = "25565"
    ENV = "production"


def load_variables():
    load_dotenv()
    variables_debug()


def get(key: Key) -> str | None:
    return os.getenv(key)


def variables_debug() -> None:
    """Prints the current environment variables for debugging."""
    logging.debug("Configuration loaded:")
    logging.debug("Path to .env: %s", env_path)
    logging.debug("DISCORD_TOKEN: %s", get(Key.DISCORD_TOKEN))
    logging.debug("API_URL: %s", get(Key.API_URL))
    logging.debug("API_PORT: %s", get(Key.API_PORT))
    logging.debug("ENV: %s\n", get(Key.ENV))
