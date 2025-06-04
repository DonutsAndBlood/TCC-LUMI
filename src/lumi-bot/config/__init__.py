import logging
import os

from dotenv import find_dotenv, load_dotenv

env_path = find_dotenv()
if not env_path:
    raise FileNotFoundError(
        "No .env file found. Please create a .env file with the required environment variables."
    )
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
API_URL = os.getenv("API_URL", "localhost")
API_PORT = os.getenv("API_PORT", "25565")
ENV = os.getenv("ENV", "production")


def variables_debug() -> None:
    """Prints the current environment variables for debugging."""
    logging.debug("Configuration loaded:")
    logging.debug("Path to .env: %s", env_path)
    logging.debug("DISCORD_TOKEN: %s", DISCORD_TOKEN)
    logging.debug("API_URL: %s", API_URL)
    logging.debug("API_PORT: %s", API_PORT)
    logging.debug("ENV: %s\n", ENV)
