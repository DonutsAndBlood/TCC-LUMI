import logging
import os
from enum import StrEnum

from dotenv import find_dotenv, load_dotenv


class Key(StrEnum):
    """Environment variables keys."""

    DISCORD_TOKEN = "DISCORD_TOKEN"
    API_URL = "API_URL"
    API_PORT = "API_PORT"
    ENV = "ENV"


class Defaults(StrEnum):
    """Default values for environment variables."""

    DISCORD_TOKEN = ""
    API_URL = "localhost"
    API_PORT = "25565"
    ENV = "production"


def load_variables():
    """Loads the environment variables from an .env file."""
    env_path = find_dotenv()
    if not env_path:
        raise FileNotFoundError(
            "No .env file found. Please create a .env file with the required environment variables."
        )

    load_dotenv(dotenv_path=env_path)
    variables_debug(env_path)


def get(key: Key) -> str:
    """Returns the value of an environment variable."""
    value = os.getenv(key, Defaults[key.value])
    if value is None or len(value) == 0:
        raise ValueError(f"No value set for variable {key}")
    return value


def variables_debug(path: str) -> None:
    """Prints the current environment variables for debugging."""
    logging.debug("Configuration loaded:")
    logging.debug("Path to .env: %s", path)
    logging.debug("DISCORD_TOKEN: %s", get(Key.DISCORD_TOKEN))
    logging.debug("API_URL: %s", get(Key.API_URL))
    logging.debug("API_PORT: %s", get(Key.API_PORT))
    logging.debug("ENV: %s\n", get(Key.ENV))
