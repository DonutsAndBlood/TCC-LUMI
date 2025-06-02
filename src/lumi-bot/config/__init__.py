import os

from dotenv import find_dotenv, load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
API_URL = os.getenv("API_URL", "localhost")
API_PORT = os.getenv("API_PORT", "25565")
ENV = os.getenv("ENV", "production")

print("Configuration loaded:")
print(find_dotenv())
print(f"DISCORD_TOKEN: {DISCORD_TOKEN}")
print(f"API_URL: {API_URL}")
print(f"API_PORT: {API_PORT}")
print(f"ENV: {ENV}\n")
