from dotenv import load_dotenv
import os

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
API_URL = os.getenv("API_URL", "localhost")
API_PORT = os.getenv("API_PORT", "25565")
ENV = os.getenv("ENV", "production")
