import asyncio
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


def initialize_logger():
    debug_mode = is_dev()
    if debug_mode:
        asyncio.get_event_loop().set_debug(True)
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


def load_variables():
    """Loads the environment variables from an .env file."""
    env_path = find_dotenv()
    if len(env_path) == 0:
        raise FileNotFoundError(
            "No .env file found. Please create a .env file with the required environment variables."
        )

    load_dotenv(dotenv_path=env_path)
    initialize_logger()
    variables_debug(env_path)


def get(key: Key) -> str:
    """Returns the value of an environment variable."""
    value = os.getenv(key, Defaults[key.value])
    if len(value) == 0:
        raise ValueError(f"No value set for variable {key}")
    return value


def is_dev() -> bool:
    """Returns True if the app is running on development mode."""
    return get(Key.ENV) == "development"


def is_debug() -> bool:
    """Returns True if debug mode is enabled."""
    return is_dev()


def variables_debug(path: str) -> None:
    """Prints the current environment variables for debugging."""
    logging.debug("Configuration loaded:")
    logging.debug("Path to .env: %s", path)
    logging.debug("DISCORD_TOKEN: %s", get(Key.DISCORD_TOKEN))
    logging.debug("API_URL: %s", get(Key.API_URL))
    logging.debug("API_PORT: %s", get(Key.API_PORT))
    logging.debug("ENV: %s\n", get(Key.ENV))
