import asyncio
from queue import Queue

from .server import sio

queue: Queue[str] = Queue()


async def send_transcript(text: str) -> None:
    """Send the audio transcript to all connected clients."""
    await sio.emit("transcript", text)


async def process_transcripts():
    while True:
        if queue.empty():
            await asyncio.sleep(1)
            continue

        text = queue.get_nowait()

        # Now you can call the original send_transcript function safely in this event loop
        await send_transcript(text)
