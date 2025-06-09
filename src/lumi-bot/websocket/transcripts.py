import asyncio
from queue import Queue

from .server import sio

queue: Queue[str] = Queue()


async def send_transcript(text: str) -> None:
    """Send the audio transcript to all connected clients."""
    await sio.emit("transcript", text)
