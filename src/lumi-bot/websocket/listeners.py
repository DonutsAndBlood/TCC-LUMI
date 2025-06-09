import logging
from typing import Any

from .server import sio

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


def load_listeners():
    pass


# if __name__ == "__main__":
#     from dotenv import load_dotenv

#     load_dotenv()
#     logging.basicConfig(
#         level=os.getenv("ENV") == "development" and logging.DEBUG or logging.INFO
#     )
#     # AccessLogger.LOG_FORMAT
#     web.run_app(app, host=config.get(Key.API_URL), port=int(config.get(Key.API_PORT)))
#     print("Starting websocket server...")
