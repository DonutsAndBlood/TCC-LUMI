import asyncio
import logging
import os
from typing import Any

import socketio
from aiohttp import web

from config import API_PORT, API_URL

app = web.Application()
sio = socketio.AsyncServer(
    async_mode="aiohttp",
    cors_allowed_origins="*",
    transports=["websocket"],
)
sio.attach(app)

# Socket.IO Admin connection
sio.instrument(auth={"username": "admin", "password": "admin123lumi"})
clients: set[str] = set()


@sio.event  # type: ignore[misc]
async def connect(sid: str, _environ: Any, _auth: Any = None) -> None:
    """Handle client connection."""
    clients.add(sid)
    logging.info("Client connected with id %s", sid)
    logging.debug("current clients: %s", ", ".join(clients))


@sio.event  # type: ignore[misc]
async def disconnect(sid: str, reason: Any) -> None:
    """Handle client disconnection."""
    if reason == sio.reason.CLIENT_DISCONNECT:
        logging.info("Client with id %s disconnected", sid)
    elif reason == sio.reason.SERVER_DISCONNECT:
        logging.info("The server disconnected the client with id %s", sid)
    else:
        logging.info("Client with id %s disconnected with reason %s", sid, reason)
    clients.remove(sid)


async def send_transcript(text: str) -> None:
    """Send the audio transcript to all connected clients."""
    await sio.emit("transcript", text)


async def start_websocket():
    logging.info("Starting Socket.IO server...")
    logging.debug("Running server with API_URL: %s", API_URL)

    try:
        runner = web.AppRunner(app)
        await runner.setup()

        sites: list[web.TCPSite] = []
        for host in [API_URL]:
            site = web.TCPSite(
                runner=runner,
                host=host,
                port=int(API_PORT),
            )
            sites.append(site)

        for site in sites:
            await site.start()

        logging.info("Socket.IO server listening on port %s", API_PORT)
    except (ValueError, TypeError):
        logging.critical(
            "Invalid API_URL or API_PORT environment variable."
            "Please check your configuration.",
            exc_info=True,
        )
        raise
    except Exception:
        logging.critical(
            "Unknown error while starting Socket.IO server",
            exc_info=True,
        )
        raise

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    logging.basicConfig(
        level=os.getenv("ENV") == "development" and logging.DEBUG or logging.INFO
    )
    # AccessLogger.LOG_FORMAT
    web.run_app(app, host=API_URL, port=int(API_PORT))
    print("Starting websocket server...")
